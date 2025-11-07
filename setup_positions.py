#!/usr/bin/env python3
"""
Initialize user positions for Written AI Chatbot
"""
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database.models import db, UserPosition, init_db
from config.settings import settings

def populate_positions():
    """Populate the database with default user positions"""
    from app import create_app
    
    positions_data = [
        # Development Team
        {"position": "Frontend Developer", "position_prefix": "FE"},
        {"position": "Backend Developer", "position_prefix": "BE"},
        {"position": "Full Stack Developer", "position_prefix": "FS"},
        {"position": "Mobile Developer", "position_prefix": "MD"},
        {"position": "DevOps Engineer", "position_prefix": "DO"},
        
        # Design & UX
        {"position": "UI/UX Designer", "position_prefix": "UX"},
        {"position": "Graphic Designer", "position_prefix": "GD"},
        {"position": "Product Designer", "position_prefix": "PD"},
        
        # Management & Leadership
        {"position": "Project Manager", "position_prefix": "PM"},
        {"position": "Product Manager", "position_prefix": "PDM"},
        {"position": "Tech Lead", "position_prefix": "TL"},
        {"position": "Engineering Manager", "position_prefix": "EM"},
        {"position": "Scrum Master", "position_prefix": "SM"},
        
        # Quality Assurance
        {"position": "QA Engineer", "position_prefix": "QA"},
        {"position": "Test Automation Engineer", "position_prefix": "TAE"},
        {"position": "QA Lead", "position_prefix": "QAL"},
        
        # Data & Analytics
        {"position": "Data Analyst", "position_prefix": "DA"},
        {"position": "Data Engineer", "position_prefix": "DE"},
        {"position": "Data Scientist", "position_prefix": "DS"},
        {"position": "Business Intelligence", "position_prefix": "BI"},
        
        # Security & Infrastructure
        {"position": "Security Engineer", "position_prefix": "SE"},
        {"position": "System Administrator", "position_prefix": "SA"},
        {"position": "Cloud Engineer", "position_prefix": "CE"},
        {"position": "Site Reliability Engineer", "position_prefix": "SRE"},
        
        # Business & Strategy
        {"position": "Business Analyst", "position_prefix": "BA"},
        {"position": "Product Owner", "position_prefix": "PO"},
        {"position": "Solution Architect", "position_prefix": "ARCH"},
        {"position": "Technical Writer", "position_prefix": "TW"},
        
        # Customer & Support
        {"position": "Customer Success", "position_prefix": "CS"},
        {"position": "Technical Support", "position_prefix": "TS"},
        {"position": "Sales Engineer", "position_prefix": "SEN"},
    ]
    
    print("🚀 Creating Flask app and initializing database...")
    app = create_app()
    
    with app.app_context():
        print("📝 Adding user positions...")
        added_count = 0
        
        for pos_data in positions_data:
            # Check if position already exists
            existing = UserPosition.query.filter_by(position_name=pos_data["position"]).first()
            if not existing:
                position = UserPosition(
                    position_name=pos_data["position"],
                    position_prefix=pos_data["position_prefix"]
                )
                db.session.add(position)
                added_count += 1
                print(f"  ✅ Added: {pos_data['position']} ({pos_data['position_prefix']})")
            else:
                print(f"  ⚠️  Exists: {pos_data['position']} ({pos_data['position_prefix']})")
        
        try:
            db.session.commit()
            print(f"\n🎉 Successfully added {added_count} positions to database!")
            
            # Verify
            total_positions = UserPosition.query.count()
            print(f"📊 Total positions in database: {total_positions}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error committing to database: {str(e)}")
            return False
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("🏗️  Written AI Chatbot - Position Initialization")
    print("=" * 60)
    
    success = populate_positions()
    
    if success:
        print("\n✨ Position initialization complete!")
        print("💡 You can now use the application with populated positions.")
    else:
        print("\n❌ Position initialization failed!")
        sys.exit(1)
