# Written - AI-Powered Activity Generator for Taiga

**Written** is an intelligent AI-powered application designed to help development teams generate and submit daily activities to Taiga project management platforms. It solves the common problem of team members forgetting to log their daily activities, especially when facing strict time limits for activity submissions.

## 🚀 Features

- **AI-Powered Activity Generation**: Uses Google Gemini as the primary AI provider with optional OpenAI GPT or Anthropic Claude fallback to generate professional activity descriptions from brief user inputs
- **Taiga Integration**: Seamlessly connects to Taiga project management platform for automated activity submission
- **Modern Web Interface**: Clean, responsive web interface for quick activity generation and submission
- **Activity History**: Track and manage generated and submitted activities with full audit trail
- **Multi-Provider AI Support**: Intelligent fallback system supporting multiple AI providers (Gemini, OpenAI, Anthropic)
- **Enterprise Ready**: Production-ready codebase with comprehensive error handling, logging, and security features
- **Position-Aware Generation**: Context-aware activity descriptions based on user roles and project types

## 🏗️ Project Structure

```
written/
├── src/
│   ├── ai/                 # AI service integration
│   │   └── generator.py    # AI activity generation logic
│   ├── api/                # External API clients
│   │   └── taiga_client.py # Taiga API integration
│   ├── database/           # Database models and operations
│   │   └── models.py       # SQLAlchemy models
│   └── web/                # Web interface
│       └── routes.py       # Flask routes and API endpoints
├── config/
│   └── settings.py         # Application configuration
├── tests/                  # Unit and integration tests
├── app.py                  # Main application entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
└── README.md              # This file
```

## 🛠️ Technical Stack

**Written** is built with modern technologies for reliability and scalability:

- **Backend**: Python 3.8+ with Flask web framework
- **Database**: PostgreSQL for robust data management
- **AI Integration**: Multi-provider support (Google Gemini, OpenAI, Anthropic)
- **Frontend**: Responsive web interface with modern HTML/CSS/JavaScript
- **Architecture**: RESTful API design with modular component structure

## 🔧 Core Functionality

**Written** provides a comprehensive API and web interface for activity management:

### Activity Generation
- **Intelligent Content Creation**: Transforms brief user inputs into professional, detailed activity descriptions
- **Context-Aware Processing**: Considers user roles, project types, and historical data for relevant content
- **Multi-Model Support**: Leverages different AI models based on content complexity and requirements

### Taiga Integration
- **Seamless Connectivity**: Direct integration with Taiga project management platform
- **Automatic Submission**: Handles authentication, project mapping, and activity posting
- **Error Handling**: Robust retry mechanisms and detailed error reporting

### Data Management
- **Activity History**: Complete audit trail of generated and submitted activities
- **User Profiles**: Position-based customization and preferences
- **Project Mapping**: Intelligent association between development work and project structures

## 🎯 Use Cases

**Written** addresses common challenges in development team management:

### Daily Activity Tracking
- **Automated Logging**: Reduces manual effort in daily activity documentation
- **Consistency**: Ensures uniform activity description formats across team members
- **Time Management**: Helps track time allocation and project progress

### Project Management Integration
- **Centralized Reporting**: Consolidates development activities in Taiga platform
- **Team Visibility**: Provides managers with clear insight into team productivity
- **Compliance**: Maintains audit trails for project reporting and billing

### Developer Productivity
- **Reduced Administrative Burden**: Minimizes time spent on activity documentation
- **Focus Enhancement**: Allows developers to concentrate on coding rather than reporting
- **Historical Reference**: Creates searchable history of development work and decisions

## 🏗️ Architecture Overview

**Written** follows a modular, scalable architecture designed for enterprise environments:

### Component Structure
- **AI Service Layer**: Handles multiple AI provider integrations with intelligent fallback
- **API Integration Layer**: Manages external service connections (Taiga, AI providers)
- **Database Layer**: PostgreSQL-based data persistence with optimized queries
- **Web Interface**: Responsive frontend with RESTful API backend
- **Configuration Management**: Environment-based configuration with security best practices

### Security Features
- **API Key Management**: Secure handling of external service credentials
- **Input Validation**: Comprehensive sanitization of user inputs and AI responses
- **Error Handling**: Graceful degradation with detailed logging
- **Authentication**: Support for multiple Taiga authentication methods

## 🔍 Troubleshooting

### Common Issues & Solutions

**Authentication Problems:**
- **Taiga Connection Failed**: Verify Taiga URL format and credentials. Try API token method instead of username/password
- **AI Provider Error**: Check API key validity and ensure sufficient API credits/quota

**Installation Issues:**
- **Import Errors**: Activate virtual environment (`source venv/bin/activate`) and reinstall dependencies
- **Database Connection**: Verify database URL format and ensure database service is running
- **Permission Errors**: Check file permissions and ensure proper write access to project directory

**Runtime Issues:**
- **Empty Positions List**: Run `python3 setup_positions.py` to initialize user positions
- **Port Already in Use**: Change `FLASK_PORT` in `.env` or stop conflicting services

### Debug Mode
Enable detailed logging for troubleshooting:
```bash
# Set debug level in .env
LOG_LEVEL=DEBUG

# Or export temporarily
export LOG_LEVEL=DEBUG
python3 app.py
```

### Health Check
Verify system status:
```bash
# Check application health
curl http://localhost:5000/api/health

# Test database connection
python3 -c "from app import create_app; app = create_app(); print('✅ Database OK')"
```

## 🚀 Development & Roadmap

### Current Status
- ✅ Core AI-powered activity generation
- ✅ Multi-provider AI support (Gemini, OpenAI, Anthropic)
- ✅ Taiga platform integration
- ✅ PostgreSQL and SQLite database support
- ✅ RESTful API endpoints
- ✅ Position-aware activity generation
- ✅ Web-based user interface

### Planned Features
- **Enhanced UI/UX**: Modern, responsive interface improvements
- **User Authentication**: Multi-user support with role-based access
- **Activity Templates**: Pre-defined templates for common development tasks
- **Batch Processing**: Import/export capabilities for bulk activity management
- **Analytics Dashboard**: Team productivity insights and reporting
- **Mobile Support**: Progressive Web App (PWA) capabilities
- **Integration Expansion**: Support for Jira, Asana, GitHub, and other platforms

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the Repository**
   ```bash
   git fork https://github.com/DamiaRalitsa/written-io.git
   ```

2. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Development Setup**
   ```bash
   # Install development dependencies
   pip install -r requirements.txt
   pip install -r requirements-optional.txt
   
   # Run tests
   python -m pytest tests/
   ```

4. **Submit Pull Request**
   - Ensure tests pass
   - Include clear description of changes
   - Follow existing code style conventions

## � License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## � Issues & Support

- **Bug Reports**: [GitHub Issues](https://github.com/DamiaRalitsa/written-io/issues)
- **Feature Requests**: [GitHub Discussions](https://github.com/DamiaRalitsa/written-io/discussions)
- **Documentation**: Check the `docs/` directory for detailed guides

## ⭐ Acknowledgments

- Google Gemini for AI-powered content generation
- Taiga team for the excellent project management platform
- The open-source community for inspiration and tools

---

**Written** - *Streamlining daily activity tracking with AI intelligence.* 🎯
