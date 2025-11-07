"""
Main application entry point for Written AI Chatbot
"""

from flask import Flask
from flask_cors import CORS
from config.settings import settings
from src.web.routes import bp as web_bp
from src.database.models import init_db
from loguru import logger
import sys


def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Configure Flask
    app.config['SECRET_KEY'] = settings.secret_key
    app.config['SQLALCHEMY_DATABASE_URI'] = settings.database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Configure PostgreSQL-specific settings if using PostgreSQL
    if settings.database_url.startswith('postgresql://'):
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_size': 10,
            'pool_timeout': 20,
            'pool_recycle': 3600,
            'max_overflow': 20,
            'pool_pre_ping': True
        }
    
    # Enable CORS
    CORS(app)
    
    # Configure logging
    logger.remove()
    logger.add(sys.stderr, level=settings.log_level)
    logger.add("logs/written.log", rotation="1 day", level=settings.log_level)
    
    # Initialize database
    init_db(app)
    
    # Register blueprints
    app.register_blueprint(web_bp)
    
    logger.info("Written AI Chatbot application initialized")
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='127.0.0.1', port=5001)
