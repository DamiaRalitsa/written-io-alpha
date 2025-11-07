"""
Database models for Written AI Chatbot
Supports both PostgreSQL and SQLite
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from typing import Optional
from config.settings import settings
from loguru import logger

db = SQLAlchemy()


def init_db(app):
    """Initialize database with Flask app"""
    db.init_app(app)
    
    # Log database type being used
    db_url = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if db_url.startswith('postgresql://'):
        logger.info("Database: Using PostgreSQL")
    elif db_url.startswith('sqlite://'):
        logger.info("Database: Using SQLite")
    else:
        logger.warning(f"Database: Unknown database type: {db_url}")
    
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database: All tables created successfully")
        except Exception as e:
            logger.error(f"Database: Failed to create tables: {str(e)}")
            raise


class UserPosition(db.Model):
    """User position/role definitions"""
    __tablename__ = 'user_positions'
    
    id = db.Column(db.Integer, primary_key=True)
    position_name = db.Column(db.String(100), unique=True, nullable=False)
    position_prefix = db.Column(db.String(10), nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<UserPosition {self.position_name} ({self.position_prefix})>'


class User(db.Model):
    """User model for storing user preferences and authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    taiga_user_id = db.Column(db.Integer, nullable=True)
    position_id = db.Column(db.Integer, db.ForeignKey('user_positions.id'), nullable=True)
    position = db.Column(db.String(100), nullable=True)  # Keep for backward compatibility
    position_prefix = db.Column(db.String(10), nullable=True)  # Keep for backward compatibility
    preferred_ai_model = db.Column(db.String(50), default='gpt-3.5-turbo')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    user_position = db.relationship('UserPosition', backref='users', lazy=True)
    activities = db.relationship('Activity', backref='user', lazy=True)
    
    def get_activity_prefix(self):
        """Get the activity prefix for this user"""
        return f"[{self.position_prefix}]" if self.position_prefix else ""
    
    def format_activity_title(self, title):
        """Format activity title with position prefix"""
        prefix = self.get_activity_prefix()
        if prefix and not title.startswith('['):
            return f"{prefix} {title}"
        return title
    
    def __repr__(self):
        return f'<User {self.username} ({self.position or "No Position"})>'


class Project(db.Model):
    """Project model for Taiga projects"""
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    taiga_project_id = db.Column(db.Integer, unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    activities = db.relationship('Activity', backref='project', lazy=True)
    
    def __repr__(self):
        return f'<Project {self.name}>'


class Activity(db.Model):
    """Activity model for storing generated and submitted activities"""
    __tablename__ = 'activities'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    
    # Activity details
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    hours_spent = db.Column(db.Float, nullable=False, default=0.0)
    activity_date = db.Column(db.Date, nullable=False)
    
    # AI generation details
    ai_generated = db.Column(db.Boolean, default=False)
    ai_model_used = db.Column(db.String(50), nullable=True)
    user_prompt = db.Column(db.Text, nullable=True)
    
    # Taiga integration
    submitted_to_taiga = db.Column(db.Boolean, default=False)
    taiga_activity_id = db.Column(db.Integer, nullable=True)
    taiga_submission_error = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Activity {self.title}>'


class AIPromptTemplate(db.Model):
    """Template for AI prompts"""
    __tablename__ = 'ai_prompt_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    template = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AIPromptTemplate {self.name}>'
