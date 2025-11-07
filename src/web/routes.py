"""
Web routes for Written AI Chatbot
Handles HTTP requests and responses for the web interface
"""

from flask import Blueprint, request, jsonify, render_template
from datetime import datetime, date
from src.ai.generator import ai_service
from src.api.taiga_client import taiga_api
from src.database.models import db, User, Project, Activity, UserPosition
from config.settings import settings
from loguru import logger
import asyncio

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    """Main chatbot interface"""
    return render_template('index.html')


@bp.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })


@bp.route('/api/generate-activity', methods=['POST'])
def generate_activity():
    """
    Generate an activity description using AI
    
    Expected JSON payload:
    {
        "user_input": "worked on bug fixes",
        "project_id": 123,
        "hours": 4.5,
        "date": "2024-01-15",
        "ai_model": "gpt-3.5-turbo"  // optional
    }
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('user_input'):
            return jsonify({
                'success': False,
                'error': 'user_input is required'
            }), 400
        
        user_input = data['user_input']
        project_id = data.get('project_id')
        hours = data.get('hours', 0.0)
        activity_date = data.get('date', date.today().isoformat())
        ai_model = data.get('ai_model')
        
        # Build context for AI generation
        context = {
            'date': activity_date,
            'estimated_hours': hours
        }
        
        # Get project info if provided
        if project_id:
            project = Project.query.filter_by(taiga_project_id=project_id).first()
            if project:
                context['project_name'] = project.name
        
        # Get current user for position prefix
        user_id = data.get('user_id', 1)
        user = User.query.get(user_id)
        
        # Add user position context
        if user and user.position:
            context['user_position'] = user.position
            context['position_prefix'] = user.position_prefix
        
        # Generate activity description using AI
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(
            ai_service.generate_activity_description(
                user_input=user_input,
                context=context,
                model=ai_model
            )
        )
        
        loop.close()
        
        if result.get('success'):
            # Apply position prefix to the generated description
            description = result['description']
            if user and user.position_prefix:
                # Check if description already has a prefix
                if not description.strip().startswith('['):
                    description = f"[{user.position_prefix}] {description}"
            
            return jsonify({
                'success': True,
                'description': description,
                'model_used': result.get('model_used'),
                'provider': result.get('provider'),
                'is_fallback': result.get('is_fallback', False),
                'position_prefix': user.position_prefix if user else None
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'AI generation failed'),
                'fallback_description': result.get('fallback_description')
            }), 500
            
    except Exception as e:
        logger.error(f"Error in generate_activity: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@bp.route('/api/generate-task', methods=['POST'])
def generate_task():
    """
    Generate a structured task backlog item (Jira-style) using AI
    
    Expected JSON payload:
    {
        "user_input": "create user authentication system",
        "task_type": "feature",  // feature, bug_fix, improvement, technical_debt, research
        "project_id": 123,
        "ai_model": "gpt-4"  // optional
    }
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('user_input'):
            return jsonify({
                'success': False,
                'error': 'user_input is required'
            }), 400
        
        user_input = data['user_input']
        task_type = data.get('task_type', 'feature')
        project_id = data.get('project_id')
        ai_model = data.get('ai_model')
        
        # Validate task type
        valid_task_types = ['feature', 'bug_fix', 'improvement', 'technical_debt', 'research']
        if task_type not in valid_task_types:
            return jsonify({
                'success': False,
                'error': f'Invalid task_type. Must be one of: {", ".join(valid_task_types)}'
            }), 400
        
        # Build context for AI generation
        context = {}
        
        # Get project info if provided
        if project_id:
            project = Project.query.filter_by(taiga_project_id=project_id).first()
            if project:
                context['project_name'] = project.name
        
        # Get current user for position context
        user_id = data.get('user_id', 1)
        user = User.query.get(user_id)
        
        # Add user position context
        if user and user.position:
            context['user_position'] = user.position
            context['position_prefix'] = user.position_prefix
        
        # Generate structured task using AI
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(
            ai_service.generate_task_backlog_item(
                user_input=user_input,
                context=context,
                model=ai_model,
                task_type=task_type
            )
        )
        
        loop.close()
        
        if result.get('success'):
            task_data = result.get('task_data', {})
            
            return jsonify({
                'success': True,
                'task': task_data,
                'model_used': result.get('model_used'),
                'provider': result.get('provider'),
                'task_type': task_type,
                'is_fallback': result.get('is_fallback', False)
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Task generation failed'),
                'fallback_task': result.get('fallback_task')
            }), 500
            
    except Exception as e:
        logger.error(f"Error in generate_task: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@bp.route('/api/submit-activity', methods=['POST'])
def submit_activity():
    """
    Submit an activity to Taiga
    
    Expected JSON payload:
    {
        "project_id": 123,
        "description": "Fixed authentication bug in login module",
        "hours": 4.5,
        "date": "2024-01-15",
        "user_id": 456  // optional
    }
    """
    try:
        data = request.get_json()
        
        required_fields = ['project_id', 'description', 'hours', 'date']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'{field} is required'
                }), 400
        
        project_id = data['project_id']
        description = data['description']
        hours = float(data['hours'])
        activity_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        user_id = data.get('user_id')
        
        # Submit to Taiga
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Ensure authentication
        auth_success = loop.run_until_complete(taiga_api.authenticate())
        if not auth_success:
            return jsonify({
                'success': False,
                'error': 'Failed to authenticate with Taiga'
            }), 401
        
        # Submit the activity
        result = loop.run_until_complete(
            taiga_api.submit_activity(
                project_id=project_id,
                description=description,
                hours=hours,
                activity_date=activity_date,
                user_id=user_id
            )
        )
        
        loop.close()
        
        # Get user for position prefix
        current_user = User.query.get(user_id or 1)
        
        # Apply position prefix to title if not already present
        title = description[:200]  # Truncate for title
        if current_user and current_user.position_prefix:
            title = current_user.format_activity_title(title)
        
        # Store activity in local database
        activity = Activity(
            user_id=user_id or 1,  # Default user for now
            project_id=None,  # We'll need to map this
            title=title,
            description=description,
            hours_spent=hours,
            activity_date=activity_date,
            submitted_to_taiga=result.get('success', False),
            taiga_activity_id=result.get('taiga_id'),
            taiga_submission_error=result.get('error'),
            ai_generated=True  # Mark as generated since it came through our system
        )
        
        db.session.add(activity)
        db.session.commit()
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in submit_activity: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@bp.route('/api/projects')
def get_projects():
    """Get list of user's projects from Taiga"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Ensure authentication
        auth_success = loop.run_until_complete(taiga_api.authenticate())
        if not auth_success:
            return jsonify({
                'success': False,
                'error': 'Failed to authenticate with Taiga'
            }), 401
        
        # Get projects
        projects = loop.run_until_complete(taiga_api.get_user_projects())
        loop.close()
        
        return jsonify({
            'success': True,
            'projects': projects
        })
        
    except Exception as e:
        logger.error(f"Error in get_projects: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch projects'
        }), 500


@bp.route('/api/user-positions')
def get_user_positions():
    """Get available user positions"""
    try:
        positions = UserPosition.query.filter_by(is_active=True).all()
        
        positions_data = []
        for position in positions:
            positions_data.append({
                'id': position.id,
                'position_name': position.position_name,
                'position_prefix': position.position_prefix,
                'description': position.description
            })
        
        return jsonify({
            'success': True,
            'positions': positions_data
        })
        
    except Exception as e:
        logger.error(f"Error in get_user_positions: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch positions'
        }), 500


@bp.route('/api/set-user-position', methods=['POST'])
def set_user_position():
    """Set user position"""
    try:
        data = request.get_json()
        
        if not data or not data.get('position_id'):
            return jsonify({
                'success': False,
                'error': 'position_id is required'
            }), 400
        
        position_id = data['position_id']
        user_id = data.get('user_id', 1)  # Default user for now
        
        # Get position details
        position = UserPosition.query.get(position_id)
        if not position:
            return jsonify({
                'success': False,
                'error': 'Position not found'
            }), 404
        
        # Get or create user
        user = User.query.get(user_id)
        if not user:
            # Create default user if doesn't exist
            user = User(
                username='default_user',
                email='user@example.com',
                position=position.position_name,
                position_prefix=position.position_prefix
            )
            db.session.add(user)
        else:
            # Update existing user
            user.position = position.position_name
            user.position_prefix = position.position_prefix
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'position': user.position,
                'position_prefix': user.position_prefix,
                'activity_prefix': user.get_activity_prefix()
            }
        })
        
    except Exception as e:
        logger.error(f"Error in set_user_position: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to set user position'
        }), 500


@bp.route('/api/add-position', methods=['POST'])
def add_position():
    """Add a new position"""
    try:
        data = request.get_json()
        
        required_fields = ['position_name', 'position_prefix']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'{field} is required'
                }), 400
        
        position_name = data['position_name']
        position_prefix = data['position_prefix']
        description = data.get('description', '')
        
        # Check if position already exists
        existing_position = UserPosition.query.filter_by(position_name=position_name).first()
        if existing_position:
            return jsonify({
                'success': False,
                'error': 'Position already exists'
            }), 400
        
        # Create new position
        new_position = UserPosition(
            position_name=position_name,
            position_prefix=position_prefix,
            description=description,
            is_active=True
        )
        
        db.session.add(new_position)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'position': {
                'id': new_position.id,
                'position_name': new_position.position_name,
                'position_prefix': new_position.position_prefix,
                'description': new_position.description
            }
        })
        
    except Exception as e:
        logger.error(f"Error in add_position: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to add position'
        }), 500


@bp.route('/api/current-user')
def get_current_user():
    """Get current user information"""
    try:
        # For now, return default user (user_id=1)
        # In a real app, you'd get this from session/auth
        user = User.query.get(1)
        
        if not user:
            return jsonify({
                'success': True,
                'user': None
            })
        
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'position': user.position,
                'position_prefix': user.position_prefix,
                'activity_prefix': user.get_activity_prefix()
            }
        })
        
    except Exception as e:
        logger.error(f"Error in get_current_user: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch user information'
        }), 500


@bp.route('/api/activities')
def get_activities():
    """Get user's recent activities"""
    try:
        # Get query parameters
        project_id = request.args.get('project_id', type=int)
        limit = request.args.get('limit', default=20, type=int)
        
        # Query local database
        query = Activity.query.order_by(Activity.created_at.desc())
        
        if project_id:
            query = query.filter_by(project_id=project_id)
        
        activities = query.limit(limit).all()
        
        # Convert to JSON-serializable format
        activities_data = []
        for activity in activities:
            activities_data.append({
                'id': activity.id,
                'title': activity.title,
                'description': activity.description,
                'hours_spent': activity.hours_spent,
                'activity_date': activity.activity_date.isoformat(),
                'ai_generated': activity.ai_generated,
                'submitted_to_taiga': activity.submitted_to_taiga,
                'created_at': activity.created_at.isoformat(),
                'user_position': activity.user.position if activity.user else None,
                'position_prefix': activity.user.position_prefix if activity.user else None
            })
        
        return jsonify({
            'success': True,
            'activities': activities_data
        })
        
    except Exception as e:
        logger.error(f"Error in get_activities: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch activities'
        }), 500
