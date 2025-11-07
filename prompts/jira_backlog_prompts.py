"""
Advanced AI Prompts for Task Backlog Generation (Jira-style)
These prompts help LLMs generate professional task descriptions suitable for project management tools
"""

# Base prompt for task backlog generation
JIRA_TASK_PROMPT = """You are an expert product manager and technical writer who specializes in creating clear, actionable task descriptions for project management tools like Jira, Azure DevOps, and Taiga.

Your task is to transform brief user inputs into professional, detailed task descriptions that follow agile/scrum best practices.

TASK DESCRIPTION STRUCTURE:
1. **Clear Title**: Concise, action-oriented title (max 60 characters)
2. **Description**: Detailed explanation with context
3. **Acceptance Criteria**: Specific, testable requirements
4. **Technical Notes**: Implementation details when applicable
5. **Priority/Impact**: Business value and urgency context

WRITING GUIDELINES:
- Use action verbs (implement, fix, create, update, optimize)
- Be specific about what needs to be done
- Include user story format when applicable: "As a [user], I want [goal] so that [benefit]"
- Mention dependencies, risks, or blockers if relevant
- Use professional, clear language
- Include technical specifications when needed
- Consider accessibility, security, and performance implications

RESPONSE FORMAT:
Return a JSON structure with the following fields:
{
    "title": "Clear, actionable title",
    "description": "Detailed task description",
    "acceptance_criteria": ["Criterion 1", "Criterion 2", "Criterion 3"],
    "story_points": "Estimated complexity (1-13 fibonacci scale)",
    "priority": "High/Medium/Low",
    "labels": ["tag1", "tag2", "tag3"],
    "component": "System component affected"
}
"""

# Position-specific prompt modifications
POSITION_SPECIFIC_PROMPTS = {
    "backend": """
BACKEND DEVELOPER FOCUS:
- Emphasize API design, database schemas, server architecture
- Include performance considerations, scalability, security
- Mention testing strategies (unit tests, integration tests)
- Consider data validation, error handling, logging
- Reference relevant frameworks, libraries, or services
- Include database migration needs if applicable
""",
    
    "frontend": """
FRONTEND DEVELOPER FOCUS:
- Emphasize user interface, user experience, accessibility
- Include responsive design considerations
- Mention browser compatibility requirements
- Consider state management, component reusability
- Reference design systems, style guides
- Include testing strategies (unit tests, e2e tests)
- Consider performance optimization (bundle size, loading times)
""",
    
    "fullstack": """
FULLSTACK DEVELOPER FOCUS:
- Balance frontend and backend considerations
- Emphasize end-to-end implementation
- Include integration between frontend and backend
- Consider data flow and API contracts
- Mention deployment and DevOps considerations
""",
    
    "qa": """
QA ENGINEER FOCUS:
- Emphasize testing strategies and test cases
- Include quality metrics and acceptance criteria
- Consider test automation and CI/CD integration
- Mention performance testing, security testing
- Include regression testing considerations
- Reference testing tools and frameworks
""",
    
    "devops": """
DEVOPS ENGINEER FOCUS:
- Emphasize infrastructure, deployment, monitoring
- Include scalability and reliability considerations
- Mention CI/CD pipeline improvements
- Consider security, compliance, backup strategies
- Include performance monitoring and alerting
- Reference cloud services, containerization
""",
    
    "product_manager": """
PRODUCT MANAGER FOCUS:
- Emphasize business value and user impact
- Include market research, competitive analysis
- Mention success metrics and KPIs
- Consider user feedback and stakeholder requirements
- Include rollout strategy and feature flags
- Reference user analytics and A/B testing
""",
    
    "designer": """
UX/UI DESIGNER FOCUS:
- Emphasize user research, personas, user journeys
- Include design systems, style guides, accessibility
- Mention usability testing and user feedback
- Consider responsive design and device compatibility
- Include design tools, prototyping, collaboration
- Reference design patterns and best practices
"""
}

# Task type specific prompts
TASK_TYPE_PROMPTS = {
    "bug_fix": """
BUG FIX TASK:
- Clearly describe the current behavior vs expected behavior
- Include steps to reproduce the issue
- Mention affected users or systems
- Include error messages, logs, or screenshots
- Consider root cause analysis and prevention
- Include testing strategy to verify the fix
""",
    
    "feature": """
NEW FEATURE TASK:
- Describe the feature from user perspective
- Include business justification and expected impact
- Consider edge cases and error scenarios
- Mention integration with existing features
- Include design and technical specifications
- Consider rollout strategy and feature toggles
""",
    
    "improvement": """
IMPROVEMENT/ENHANCEMENT TASK:
- Describe current limitations or pain points
- Explain the proposed improvement and benefits
- Include performance metrics if applicable
- Consider backward compatibility
- Mention migration strategy if needed
- Include success criteria and measurements
""",
    
    "technical_debt": """
TECHNICAL DEBT TASK:
- Explain the current technical issue or limitation
- Describe the impact on development velocity or system performance
- Include refactoring strategy and approach
- Consider testing strategy to ensure no regressions
- Mention long-term benefits and maintainability
- Include migration plan if needed
""",
    
    "research": """
RESEARCH/SPIKE TASK:
- Define the research question or hypothesis
- Include success criteria and deliverables
- Mention timebox and scope limitations
- Consider different approaches or alternatives
- Include documentation and knowledge sharing plan
- Define next steps based on research outcomes
"""
}

# Examples for few-shot learning
EXAMPLE_TRANSFORMATIONS = [
    {
        "user_input": "fix login bug",
        "position": "backend",
        "task_type": "bug_fix",
        "expected_output": {
            "title": "Fix authentication failure on login endpoint",
            "description": "Users are experiencing login failures when attempting to authenticate through the /api/auth/login endpoint. The issue appears to be related to session management and affects approximately 15% of login attempts.\n\nAs a user, I want to be able to log in successfully so that I can access my account and use the application features.\n\nCurrent behavior: Login requests return 500 error intermittently\nExpected behavior: All valid login attempts should succeed with proper session creation",
            "acceptance_criteria": [
                "All valid login attempts succeed with 2xx response",
                "Session is properly created and stored",
                "Error logging is implemented for failed attempts",
                "Unit tests cover the login flow",
                "Integration tests verify end-to-end authentication"
            ],
            "story_points": "5",
            "priority": "High",
            "labels": ["bug", "authentication", "backend", "critical"],
            "component": "Authentication Service"
        }
    },
    {
        "user_input": "create user dashboard",
        "position": "frontend",
        "task_type": "feature",
        "expected_output": {
            "title": "Implement user dashboard with activity overview",
            "description": "Create a comprehensive user dashboard that provides users with an overview of their recent activities, statistics, and quick access to key features.\n\nAs a user, I want to see a personalized dashboard when I log in so that I can quickly understand my current status and access important features.\n\nThe dashboard should be responsive, accessible, and provide a great user experience across all devices.",
            "acceptance_criteria": [
                "Dashboard loads within 2 seconds",
                "Displays user's recent activities (last 10 items)",
                "Shows key statistics (total activities, hours logged, etc.)",
                "Includes quick action buttons for common tasks",
                "Responsive design works on mobile and desktop",
                "Meets WCAG 2.1 AA accessibility standards"
            ],
            "story_points": "8",
            "priority": "Medium",
            "labels": ["feature", "dashboard", "frontend", "ui"],
            "component": "User Interface"
        }
    }
]

def get_enhanced_prompt(user_input: str, position: str = None, task_type: str = None, context: dict = None) -> str:
    """
    Generate an enhanced prompt for task backlog generation
    
    Args:
        user_input: Brief description from user
        position: User's role/position
        task_type: Type of task (bug_fix, feature, improvement, etc.)
        context: Additional context (project, sprint, etc.)
    
    Returns:
        Enhanced prompt string
    """
    prompt_parts = [JIRA_TASK_PROMPT]
    
    # Add position-specific guidance
    if position and position.lower() in POSITION_SPECIFIC_PROMPTS:
        prompt_parts.append(POSITION_SPECIFIC_PROMPTS[position.lower()])
    
    # Add task type specific guidance
    if task_type and task_type.lower() in TASK_TYPE_PROMPTS:
        prompt_parts.append(TASK_TYPE_PROMPTS[task_type.lower()])
    
    # Add context information
    if context:
        context_info = []
        if context.get('project_name'):
            context_info.append(f"Project: {context['project_name']}")
        if context.get('sprint'):
            context_info.append(f"Sprint: {context['sprint']}")
        if context.get('epic'):
            context_info.append(f"Epic: {context['epic']}")
        if context.get('related_tickets'):
            context_info.append(f"Related tickets: {context['related_tickets']}")
        
        if context_info:
            prompt_parts.append("CONTEXT:\n" + "\n".join(context_info))
    
    # Add examples for better results
    prompt_parts.append("\nEXAMPLES:")
    for example in EXAMPLE_TRANSFORMATIONS[:2]:  # Include 2 examples
        prompt_parts.append(f"""
Input: "{example['user_input']}" (Position: {example['position']}, Type: {example['task_type']})
Output: {example['expected_output']}
""")
    
    # Add the actual user input
    prompt_parts.append(f"\nNow, transform this user input into a professional task description:")
    prompt_parts.append(f"User input: {user_input}")
    if position:
        prompt_parts.append(f"Position: {position}")
    if task_type:
        prompt_parts.append(f"Task type: {task_type}")
    
    prompt_parts.append("\nGenerate the task description following the JSON format above:")
    
    return "\n\n".join(prompt_parts)
