"""
Taiga API integration for Written chatbot
Handles communication with Taiga project management platform
"""

import requests
from typing import Optional, Dict, List, Any
from datetime import datetime, date
from config.settings import settings
from loguru import logger


class TaigaAPIError(Exception):
    """Custom exception for Taiga API errors"""
    pass


class TaigaAPI:
    """Taiga API client for project management integration"""
    
    def __init__(self):
        self.base_url = settings.taiga_base_url
        self.auth_token = None
        self.session = requests.Session()
        
    async def authenticate(self) -> bool:
        """
        Authenticate with Taiga API
        
        Returns:
            bool: True if authentication successful
        """
        try:
            # Use token if available
            if settings.taiga_auth_token:
                self.auth_token = settings.taiga_auth_token
                self.session.headers.update({
                    'Authorization': f'Bearer {self.auth_token}',
                    'Content-Type': 'application/json'
                })
                return await self._verify_token()
            
            # Use username/password authentication
            elif settings.taiga_username and settings.taiga_password:
                return await self._authenticate_with_credentials()
            
            else:
                logger.error("No Taiga authentication credentials provided")
                return False
                
        except Exception as e:
            logger.error(f"Taiga authentication failed: {str(e)}")
            return False
    
    async def _authenticate_with_credentials(self) -> bool:
        """Authenticate using username and password"""
        auth_url = f"{self.base_url}/api/v1/auth"
        
        payload = {
            "username": settings.taiga_username,
            "password": settings.taiga_password,
            "type": "normal"
        }
        
        response = self.session.post(auth_url, json=payload)
        
        if response.status_code == 200:
            auth_data = response.json()
            self.auth_token = auth_data.get('auth_token')
            
            self.session.headers.update({
                'Authorization': f'Bearer {self.auth_token}',
                'Content-Type': 'application/json'
            })
            
            logger.info("Successfully authenticated with Taiga")
            return True
        else:
            logger.error(f"Taiga authentication failed: {response.status_code} - {response.text}")
            return False
    
    async def _verify_token(self) -> bool:
        """Verify the current auth token is valid"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/users/me")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Token verification failed: {str(e)}")
            return False
    
    async def get_user_projects(self) -> List[Dict[str, Any]]:
        """
        Get list of projects for the authenticated user
        
        Returns:
            List of project dictionaries
        """
        try:
            response = self.session.get(f"{self.base_url}/api/v1/projects")
            
            if response.status_code == 200:
                return response.json()
            else:
                raise TaigaAPIError(f"Failed to fetch projects: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error fetching user projects: {str(e)}")
            raise TaigaAPIError(str(e))
    
    async def get_project_details(self, project_id: int) -> Dict[str, Any]:
        """
        Get detailed information about a specific project
        
        Args:
            project_id: Taiga project ID
            
        Returns:
            Project details dictionary
        """
        try:
            response = self.session.get(f"{self.base_url}/api/v1/projects/{project_id}")
            
            if response.status_code == 200:
                return response.json()
            else:
                raise TaigaAPIError(f"Failed to fetch project details: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error fetching project details: {str(e)}")
            raise TaigaAPIError(str(e))
    
    async def submit_activity(
        self,
        project_id: int,
        description: str,
        hours: float,
        activity_date: date,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Submit an activity/time entry to Taiga
        
        Args:
            project_id: Taiga project ID
            description: Activity description
            hours: Hours spent on the activity
            activity_date: Date of the activity
            user_id: Optional user ID (defaults to authenticated user)
            
        Returns:
            Dictionary with submission result
        """
        try:
            # Format date for Taiga API
            formatted_date = activity_date.strftime('%Y-%m-%d')
            
            payload = {
                'project': project_id,
                'description': description,
                'hours': hours,
                'date': formatted_date
            }
            
            if user_id:
                payload['user'] = user_id
            
            # Submit to Taiga time tracking endpoint
            response = self.session.post(
                f"{self.base_url}/api/v1/time-entries",
                json=payload
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                logger.info(f"Successfully submitted activity to Taiga: {result.get('id')}")
                return {
                    'success': True,
                    'taiga_id': result.get('id'),
                    'data': result
                }
            else:
                error_msg = f"Failed to submit activity: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {
                    'success': False,
                    'error': error_msg,
                    'status_code': response.status_code
                }
                
        except Exception as e:
            error_msg = f"Error submitting activity to Taiga: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    
    async def get_user_activities(
        self,
        project_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Get user's activities/time entries from Taiga
        
        Args:
            project_id: Optional project ID filter
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            List of activity dictionaries
        """
        try:
            params = {}
            
            if project_id:
                params['project'] = project_id
            if start_date:
                params['date__gte'] = start_date.strftime('%Y-%m-%d')
            if end_date:
                params['date__lte'] = end_date.strftime('%Y-%m-%d')
            
            response = self.session.get(
                f"{self.base_url}/api/v1/time-entries",
                params=params
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise TaigaAPIError(f"Failed to fetch activities: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error fetching user activities: {str(e)}")
            raise TaigaAPIError(str(e))


# Global Taiga API instance
taiga_api = TaigaAPI()
