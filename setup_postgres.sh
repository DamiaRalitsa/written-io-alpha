#!/bin/bash

# Written AI Chatbot - PostgreSQL Setup Script
# This script sets up the application with PostgreSQL support

set -e  # Exit on any error

echo "🐘 Written AI Chatbot - PostgreSQL Setup"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

echo -e "${BLUE}📁 Project directory: $SCRIPT_DIR${NC}"

# Check if PostgreSQL is running
check_postgres() {
    echo -e "${BLUE}🔍 Checking PostgreSQL connection...${NC}"
    
    # Try to connect to PostgreSQL on port 5433 (your Docker setup)
    if pg_isready -h localhost -p 5433 -U postgres >/dev/null 2>&1; then
        echo -e "${GREEN}✅ PostgreSQL is running on port 5433${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  PostgreSQL not detected on port 5433${NC}"
        echo -e "${YELLOW}Please make sure your PostgreSQL Docker container is running:${NC}"
        echo "   docker-compose up -d postgres"
        echo ""
        echo -e "${YELLOW}Or if you're using Docker directly:${NC}"
        echo "   docker run -d --name postgres \\"
        echo "     -e POSTGRES_USER=postgres \\"
        echo "     -e POSTGRES_PASSWORD=password \\"
        echo "     -e POSTGRES_DB=test \\"
        echo "     -p 5433:5432 \\"
        echo "     postgres:13.3-alpine"
        return 1
    fi
}

# Setup virtual environment
setup_venv() {
    echo -e "${BLUE}🐍 Setting up Python virtual environment...${NC}"
    
    if [ -d "$SCRIPT_DIR/venv" ]; then
        echo -e "${GREEN}✅ Virtual environment already exists${NC}"
    else
        echo -e "${YELLOW}📦 Creating virtual environment...${NC}"
        python3 -m venv venv
    fi
    
    echo -e "${BLUE}🔧 Activating virtual environment...${NC}"
    source "$SCRIPT_DIR/venv/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip
    
    echo -e "${GREEN}✅ Virtual environment ready${NC}"
}

# Install dependencies
install_dependencies() {
    echo -e "${BLUE}📦 Installing Python dependencies...${NC}"
    
    # Install PostgreSQL adapter first
    echo -e "${YELLOW}🐘 Installing PostgreSQL adapter...${NC}"
    pip install psycopg2-binary
    
    # Install other dependencies
    echo -e "${YELLOW}📚 Installing application dependencies...${NC}"
    pip install -r requirements.txt
    
    echo -e "${GREEN}✅ All dependencies installed${NC}"
}

# Setup environment file
setup_env() {
    echo -e "${BLUE}⚙️ Setting up environment configuration...${NC}"
    
    if [ ! -f "$SCRIPT_DIR/.env" ]; then
        echo -e "${YELLOW}📝 Creating .env file from template...${NC}"
        cp .env.example .env
        
        # Update database URL for PostgreSQL
        sed -i 's|DATABASE_URL=sqlite:///written.db|DATABASE_URL=postgresql://postgres:password@localhost:5433/test|g' .env
        
        echo -e "${GREEN}✅ Environment file created${NC}"
        echo -e "${YELLOW}📝 Please edit .env file to configure your settings:${NC}"
        echo "   - Add your AI API keys (OpenAI or Anthropic)"
        echo "   - Update Taiga credentials"
        echo "   - Modify database settings if needed"
    else
        echo -e "${GREEN}✅ Environment file already exists${NC}"
        
        # Check if DATABASE_URL is set to PostgreSQL
        if grep -q "postgresql://" .env; then
            echo -e "${GREEN}✅ PostgreSQL configuration detected${NC}"
        else
            echo -e "${YELLOW}⚠️  Database URL in .env file is not set to PostgreSQL${NC}"
            echo -e "${YELLOW}💡 Consider updating DATABASE_URL in .env to:${NC}"
            echo "   DATABASE_URL=postgresql://postgres:password@localhost:5433/test"
        fi
    fi
}

# Setup database
setup_database() {
    echo -e "${BLUE}🗄️ Setting up PostgreSQL database...${NC}"
    
    # Test database connection
    echo -e "${YELLOW}🔍 Testing database connection...${NC}"
    python3 -c "
import sys
sys.path.append('.')
try:
    from src.database.postgres_manager import get_database_manager
    db = get_database_manager()
    if db.test_connection():
        print('✅ Database connection successful')
    else:
        print('❌ Database connection failed')
        sys.exit(1)
except Exception as e:
    print(f'❌ Database connection error: {e}')
    sys.exit(1)
"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Database connection successful${NC}"
        
        # Run migrations
        echo -e "${YELLOW}🔄 Running database migrations...${NC}"
        python3 migrate_database.py
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Database setup completed${NC}"
        else
            echo -e "${RED}❌ Database migration failed${NC}"
            return 1
        fi
    else
        echo -e "${RED}❌ Database connection failed${NC}"
        return 1
    fi
}

# Test application
test_application() {
    echo -e "${BLUE}🧪 Testing application startup...${NC}"
    
    # Quick startup test
    timeout 10s python3 -c "
from app import create_app
app = create_app()
print('✅ Application creates successfully')
" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Application startup test passed${NC}"
    else
        echo -e "${YELLOW}⚠️ Application startup test timeout (this is normal)${NC}"
    fi
}

# Main setup process
main() {
    cd "$SCRIPT_DIR"
    
    echo -e "${BLUE}🚀 Starting setup process...${NC}"
    echo ""
    
    # Check PostgreSQL first
    if ! check_postgres; then
        echo -e "${RED}❌ Please start PostgreSQL first, then run this script again${NC}"
        exit 1
    fi
    echo ""
    
    # Setup virtual environment
    setup_venv
    echo ""
    
    # Install dependencies
    install_dependencies
    echo ""
    
    # Setup environment
    setup_env
    echo ""
    
    # Setup database
    setup_database
    echo ""
    
    # Test application
    test_application
    echo ""
    
    echo -e "${GREEN}🎉 Setup completed successfully!${NC}"
    echo ""
    echo -e "${BLUE}📋 Next steps:${NC}"
    echo "1. Edit .env file to add your API keys and Taiga credentials"
    echo "2. Start the application: ./start.sh"
    echo "3. Open your browser: http://127.0.0.1:5000"
    echo ""
    echo -e "${BLUE}🔧 Useful commands:${NC}"
    echo "• Start app: ./start.sh"
    echo "• Setup database: python3 migrate_database.py"
    echo "• Test database: python3 -c 'from src.database.postgres_manager import get_database_manager; print(get_database_manager().test_connection())'"
    echo ""
    echo -e "${GREEN}✨ Your Written AI Chatbot with PostgreSQL is ready!${NC}"
}

# Run main function
main "$@"
