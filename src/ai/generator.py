"""
AI service integration for Written chatbot
Handles communication with AI providers (OpenAI, Anthropic, etc.)
"""

from typing import Optional, Dict, Any
from config.settings import settings
from loguru import logger
import asyncio
import aiohttp
import json
import sys
import os

# Add prompts directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../prompts'))

try:
    from jira_backlog_prompts import get_enhanced_prompt, POSITION_SPECIFIC_PROMPTS
except ImportError:
    logger.warning("Could not import enhanced prompts, using fallback")
    get_enhanced_prompt = None
    POSITION_SPECIFIC_PROMPTS = {}


class AIService:
    """Base class for AI service integration"""
    
    def __init__(self):
        # Check if API keys are properly configured (not placeholder values)
        self.openai_available = (
            bool(settings.openai_api_key) and 
            settings.openai_api_key != "your_openai_api_key_here"
        )
        self.anthropic_available = (
            bool(settings.anthropic_api_key) and 
            settings.anthropic_api_key != "your_anthropic_api_key_here"
        )
        self.gemini_available = (
            bool(settings.gemini_api_key) and 
            settings.gemini_api_key.startswith("AIza")  # Valid Gemini key format
        )
        
        # Log provider availability
        logger.info(f"AI Providers available - OpenAI: {self.openai_available}, Anthropic: {self.anthropic_available}, Gemini: {self.gemini_available}")
        
        # Ensure at least one provider is available
        if not any([self.openai_available, self.anthropic_available, self.gemini_available]):
            logger.warning("No AI providers are properly configured!")
    
    async def generate_activity_description(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate an activity description based on user input
        
        Args:
            user_input: User's brief description or keywords
            context: Additional context (project, previous activities, etc.)
            model: Specific AI model to use
            
        Returns:
            Dict containing generated description and metadata
        """
        try:
            # Determine which AI service to use based on primary provider or model specification
            if model and model.startswith('gemini') and self.gemini_available:
                return await self._generate_with_gemini(user_input, context, model)
            elif model and model.startswith('gpt') and self.openai_available:
                return await self._generate_with_openai(user_input, context, model)
            elif model and model.startswith('claude') and self.anthropic_available:
                return await self._generate_with_anthropic(user_input, context, model)
            elif settings.primary_ai_provider == "gemini" and self.gemini_available:
                return await self._generate_with_gemini(user_input, context)
            elif settings.primary_ai_provider == "openai" and self.openai_available:
                return await self._generate_with_openai(user_input, context)
            elif settings.primary_ai_provider == "anthropic" and self.anthropic_available:
                return await self._generate_with_anthropic(user_input, context)
            elif self.gemini_available:
                return await self._generate_with_gemini(user_input, context)
            elif self.openai_available:
                return await self._generate_with_openai(user_input, context)
            elif self.anthropic_available:
                return await self._generate_with_anthropic(user_input, context)
            else:
                return self._fallback_generation(user_input, context)
                
        except Exception as e:
            logger.error(f"AI generation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'fallback_description': self._fallback_generation(user_input, context)['description']
            }

    async def generate_task_backlog_item(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None,
        model: Optional[str] = None,
        task_type: str = "feature"
    ) -> Dict[str, Any]:
        """
        Generate a structured task backlog item (Jira-style) based on user input
        
        Args:
            user_input: User's brief description or keywords
            context: Additional context (project, sprint, etc.)
            model: Specific AI model to use
            task_type: Type of task (bug_fix, feature, improvement, technical_debt, research)
            
        Returns:
            Dict containing structured task information
        """
        try:
            # Use enhanced prompt if available
            if get_enhanced_prompt:
                position = context.get('user_position', '').lower() if context else ''
                enhanced_prompt = get_enhanced_prompt(
                    user_input=user_input,
                    position=position,
                    task_type=task_type,
                    context=context
                )
                
                # Generate with enhanced prompt
                if model and model.startswith('gemini') and self.gemini_available:
                    result = await self._generate_structured_with_gemini(enhanced_prompt, model)
                elif model and model.startswith('gpt') and self.openai_available:
                    result = await self._generate_structured_with_openai(enhanced_prompt, model)
                elif model and model.startswith('claude') and self.anthropic_available:
                    result = await self._generate_structured_with_anthropic(enhanced_prompt, model)
                elif settings.primary_ai_provider == "gemini" and self.gemini_available:
                    result = await self._generate_structured_with_gemini(enhanced_prompt)
                elif settings.primary_ai_provider == "openai" and self.openai_available:
                    result = await self._generate_structured_with_openai(enhanced_prompt)
                elif settings.primary_ai_provider == "anthropic" and self.anthropic_available:
                    result = await self._generate_structured_with_anthropic(enhanced_prompt)
                elif self.gemini_available:
                    result = await self._generate_structured_with_gemini(enhanced_prompt)
                elif self.openai_available:
                    result = await self._generate_structured_with_openai(enhanced_prompt)
                elif self.anthropic_available:
                    result = await self._generate_structured_with_anthropic(enhanced_prompt)
                else:
                    return self._fallback_task_generation(user_input, context, task_type)
                
                # Parse JSON response
                try:
                    task_data = json.loads(result['description'])
                    return {
                        'success': True,
                        'task_data': task_data,
                        'model_used': result.get('model_used'),
                        'provider': result.get('provider'),
                        'task_type': task_type
                    }
                except json.JSONDecodeError:
                    logger.warning("Failed to parse JSON response, using fallback")
                    return self._fallback_task_generation(user_input, context, task_type)
            else:
                # Fallback to regular generation
                return await self.generate_activity_description(user_input, context, model)
                
        except Exception as e:
            logger.error(f"Task backlog generation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'fallback_task': self._fallback_task_generation(user_input, context, task_type)
            }
    
    async def _generate_with_openai(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate description using OpenAI API"""
        try:
            # Check if OpenAI is available
            if not settings.openai_api_key or settings.openai_api_key == "your_openai_api_key_here":
                raise Exception("OpenAI API key not configured")
            
            try:
                from openai import AsyncOpenAI
            except ImportError:
                raise Exception("OpenAI package not installed")
            
            # Configure OpenAI client with minimal parameters
            client = AsyncOpenAI(
                api_key=settings.openai_api_key,
                timeout=30.0
            )
            model = model or settings.openai_model
            
            # Build prompt
            prompt = self._build_prompt(user_input, context)
            
            # Make API call
            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates professional daily activity descriptions for project management."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=settings.max_activity_length,
                temperature=0.7
            )
            
            description = response.choices[0].message.content.strip()
            
            return {
                'success': True,
                'description': description,
                'model_used': model,
                'provider': 'openai',
                'token_usage': response.usage.total_tokens if hasattr(response, 'usage') else None
            }
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise
    
    async def _generate_with_anthropic(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate description using Anthropic API"""
        try:
            # Check if Anthropic is available
            if not settings.anthropic_api_key or settings.anthropic_api_key == "your_anthropic_api_key_here":
                raise Exception("Anthropic API key not configured")
            
            try:
                import anthropic
            except ImportError:
                raise Exception("Anthropic package not installed")
            
            # Configure Anthropic client with minimal parameters
            client = anthropic.Anthropic(
                api_key=settings.anthropic_api_key,
                timeout=30.0
            )
            model = model or settings.anthropic_model
            
            # Build prompt
            prompt = self._build_prompt(user_input, context)
            
            # Make API call
            response = await client.messages.create(
                model=model,
                max_tokens=settings.max_activity_length,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            description = response.content[0].text.strip()
            
            return {
                'success': True,
                'description': description,
                'model_used': model,
                'provider': 'anthropic',
                'token_usage': response.usage.total_tokens if hasattr(response, 'usage') else None
            }
            
        except Exception as e:
            logger.error(f"Anthropic API error: {str(e)}")
            raise
    
    def _build_prompt(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Build the prompt for AI generation"""
        prompt_parts = [settings.default_activity_prompt]
        
        # Add context if available
        if context:
            if context.get('user_position'):
                prompt_parts.append(f"User Role: {context['user_position']}")
            if context.get('project_name'):
                prompt_parts.append(f"Project: {context['project_name']}")
            if context.get('date'):
                prompt_parts.append(f"Date: {context['date']}")
            if context.get('estimated_hours'):
                prompt_parts.append(f"Estimated hours: {context['estimated_hours']}")
        
        # Add user input
        prompt_parts.append(f"User input: {user_input}")
        
        # Add instructions with position-specific guidance
        instructions = [
            "\nGenerate a clear, professional activity description that:",
            "- Is specific and actionable",
            "- Uses professional language",
            "- Includes relevant technical details if applicable",
            "- Is suitable for project management tracking",
            "- Is concise but informative"
        ]
        
        # Add position-specific instructions
        if context and context.get('user_position'):
            position = context['user_position'].lower()
            if 'backend' in position or 'be' in position:
                instructions.append("- Focuses on backend/server-side work (APIs, databases, services)")
            elif 'frontend' in position or 'fe' in position:
                instructions.append("- Focuses on frontend/client-side work (UI, UX, components)")
            elif 'devops' in position:
                instructions.append("- Focuses on infrastructure, deployment, and operations")
            elif 'qa' in position or 'quality' in position:
                instructions.append("- Focuses on testing, quality assurance, and bug reporting")
            elif 'design' in position or 'ui' in position:
                instructions.append("- Focuses on design, user experience, and visual elements")
            elif 'mobile' in position:
                instructions.append("- Focuses on mobile development and platform-specific features")
        
        prompt_parts.append("\n".join(instructions))
        
        return "\n\n".join(prompt_parts)
    
    async def _generate_with_gemini(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate description using Google Gemini API"""
        try:
            import google.generativeai as genai
            
            # Configure Gemini
            genai.configure(api_key=settings.gemini_api_key)
            model_name = model or settings.gemini_model
            
            # Create model instance
            model_instance = genai.GenerativeModel(model_name)
            
            # Build prompt
            prompt = self._build_prompt(user_input, context)
            
            # Make API call
            response = await asyncio.to_thread(
                model_instance.generate_content,
                prompt
            )
            
            description = response.text.strip()
            
            return {
                'success': True,
                'description': description,
                'model_used': model_name,
                'provider': 'gemini',
                'token_usage': None  # Gemini doesn't provide token usage in the same way
            }
            
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            raise

    async def _generate_structured_with_gemini(self, prompt: str, model: Optional[str] = None) -> Dict[str, Any]:
        """Generate structured response using Google Gemini API"""
        try:
            import google.generativeai as genai
            
            # Configure Gemini
            genai.configure(api_key=settings.gemini_api_key)
            model_name = model or settings.gemini_model
            
            # Create model instance
            model_instance = genai.GenerativeModel(model_name)
            
            # Make API call with JSON instruction
            full_prompt = f"{prompt}\n\nPlease respond with valid JSON only, no additional text or markdown formatting."
            
            response = await asyncio.to_thread(
                model_instance.generate_content,
                full_prompt
            )
            
            description = response.text.strip()
            
            # Clean up response if it has markdown formatting
            if description.startswith('```json'):
                description = description.replace('```json', '').replace('```', '').strip()
            elif description.startswith('```'):
                description = description.replace('```', '').strip()
            
            return {
                'success': True,
                'description': description,
                'model_used': model_name,
                'provider': 'gemini',
                'token_usage': None
            }
            
        except Exception as e:
            logger.error(f"Gemini structured API error: {str(e)}")
            raise
    
    def _fallback_generation(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Fallback generation when AI services are not available"""
        # Simple template-based generation
        description = f"Worked on: {user_input}"
        
        if context and context.get('project_name'):
            description = f"Worked on {context['project_name']}: {user_input}"
        
        return {
            'success': True,
            'description': description,
            'model_used': 'fallback',
            'provider': 'local',
            'is_fallback': True
        }

    async def _generate_structured_with_openai(self, prompt: str, model: Optional[str] = None) -> Dict[str, Any]:
        """Generate structured response using OpenAI API"""
        try:
            # Check if OpenAI is available
            if not self.openai_available:
                raise Exception("OpenAI API not configured or available")
            
            try:
                from openai import AsyncOpenAI
            except ImportError:
                raise Exception("OpenAI package not installed")
            
            # Configure OpenAI client with minimal parameters
            client = AsyncOpenAI(
                api_key=settings.openai_api_key,
                timeout=30.0
            )
            model = model or settings.openai_model
            
            # Make API call
            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a professional product manager and technical writer. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.3  # Lower temperature for more structured output
            )
            
            description = response.choices[0].message.content.strip()
            
            return {
                'success': True,
                'description': description,
                'model_used': model,
                'provider': 'openai',
                'token_usage': response.usage.total_tokens if hasattr(response, 'usage') else None
            }
            
        except Exception as e:
            logger.error(f"OpenAI structured API error: {str(e)}")
            raise

    async def _generate_structured_with_anthropic(self, prompt: str, model: Optional[str] = None) -> Dict[str, Any]:
        """Generate structured response using Anthropic API"""
        try:
            # Check if Anthropic is available
            if not self.anthropic_available:
                raise Exception("Anthropic API not configured or available")
            
            try:
                import anthropic
            except ImportError:
                raise Exception("Anthropic package not installed")
            
            # Configure Anthropic client with minimal parameters
            client = anthropic.Anthropic(
                api_key=settings.anthropic_api_key,
                timeout=30.0
            )
            model = model or settings.anthropic_model
            
            # Make API call
            response = await client.messages.create(
                model=model,
                max_tokens=1500,
                temperature=0.3,  # Lower temperature for more structured output
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            description = response.content[0].text.strip()
            
            return {
                'success': True,
                'description': description,
                'model_used': model,
                'provider': 'anthropic',
                'token_usage': response.usage.total_tokens if hasattr(response, 'usage') else None
            }
            
        except Exception as e:
            logger.error(f"Anthropic structured API error: {str(e)}")
            raise

    def _fallback_task_generation(self, user_input: str, context: Optional[Dict[str, Any]] = None, task_type: str = "feature") -> Dict[str, Any]:
        """Fallback task generation when AI services are not available"""
        
        # Determine priority based on task type
        priority_map = {
            "bug_fix": "High",
            "feature": "Medium", 
            "improvement": "Medium",
            "technical_debt": "Low",
            "research": "Low"
        }
        
        # Basic task structure
        task_data = {
            "title": f"{task_type.replace('_', ' ').title()}: {user_input}",
            "description": f"Task: {user_input}\n\nThis task was generated using fallback mode. Please review and enhance the description with more details.",
            "acceptance_criteria": [
                "Task is completed successfully",
                "Code is reviewed and tested",
                "Documentation is updated if needed"
            ],
            "story_points": "3",
            "priority": priority_map.get(task_type, "Medium"),
            "labels": [task_type.replace('_', '-'), "fallback"],
            "component": context.get('project_name', 'General') if context else 'General'
        }
        
        return {
            'success': True,
            'task_data': task_data,
            'model_used': 'fallback',
            'provider': 'local',
            'is_fallback': True,
            'task_type': task_type
        }


# Global AI service instance
ai_service = AIService()
