# PyLearnAI - Self-Learning Python Expert AI

## Overview

PyLearnAI is a self-improving Python programming assistant that continuously learns from web sources and user interactions. The system combines automated data collection from authoritative Python sources with AI-powered question answering capabilities. It features a web-based chat interface for users to ask Python programming questions and receives answers from a continuously trained language model.

The application scrapes content from Python documentation, GitHub repositories, and Stack Overflow to build a comprehensive knowledge base. This data is processed, cleaned, and used to fine-tune AI models that can provide accurate, contextual responses to Python programming queries. The system includes automated scheduling for data collection and model training, quality control mechanisms, and an admin dashboard for monitoring system performance.

## User Preferences

Preferred communication style: Simple, everyday language.
Programming languages to support: HTML, CSS, JavaScript, React, Python
Application generation: System should be able to create complete apps in these languages when requested.
Firebase integration: Use https://myaisystem-16411-default-rtdb.firebaseio.com/ for external data storage and learning enhancement.

## Recent Changes (2025-08-01)

- **Replit Migration Complete**: Successfully migrated from Replit Agent to native Replit environment
- **Database Schema Fixed**: Added missing fields (used_for_training, user_rating, started_at) to database models
- **PostgreSQL Integration**: Configured secure PostgreSQL database with proper environment variables
- **Git Integration**: All code changes committed and saved to repository permanently
- **API Keys Configured**: OpenAI, DeepSeek, and session secrets properly set up
- **Application Running**: Flask server successfully running on port 5000 with all AI features active
- **Conversational AI Enhanced**: Added human-friendly responses for greetings, basic interactions, and casual conversation
- **Generic AI Priority**: Restructured AI to be general conversational first, with programming expertise activated only when specifically asked
- **Multi-Model AI System**: Integrated both OpenAI GPT-4o and DeepSeek APIs for enhanced programming assistance
- **Intelligent Model Selection**: Automatic model selection based on task type, language, and performance analytics
- **Model Comparison Features**: Side-by-side comparison of responses from different AI models
- **Machine Learning Capabilities**: Added scikit-learn, pandas, matplotlib for advanced AI features
- **Self-Troubleshooting AI**: Implemented automatic error detection, diagnosis, and fixing
- **Web Framework Expert**: Added specialized AI for HTML, CSS, JavaScript, React, Vue, Angular
- **Integrated AI Architecture**: Combined all AI components into unified system with intelligent routing
- **Enhanced Interface**: Created comprehensive web interface with multi-model selection and analytics
- **Performance Analytics**: Real-time tracking of model performance, response times, and quality scores
- **Security Hardening**: Implemented proper client/server separation and secure configuration
- **Fallback Systems**: Automatic fallback between models when API limits are reached

## System Architecture

### Web Framework Architecture
The application uses **Flask** as the primary web framework with SQLAlchemy for database operations. The choice of Flask provides lightweight, flexible web service capabilities suitable for an AI-focused application. The modular structure separates concerns between data processing, AI models, web scraping, and user interface components.

### Database Design
The system uses **SQLite** as the default database with SQLAlchemy ORM for data modeling. Four main entities structure the data:
- **KnowledgeBase**: Stores scraped content with quality scores and source attribution
- **TrainingData**: Holds question-answer pairs for model training
- **ModelMetrics**: Tracks model performance and versioning
- **UserQueries**: Logs user interactions for analysis and improvement

This design supports both structured knowledge storage and machine learning data pipelines while maintaining data quality through scoring mechanisms.

### AI Model Management
The system implements a **transformer-based architecture** using Hugging Face's transformers library with Microsoft's DialoGPT as the base model. The ModelManager handles versioning, backups, and model deployment, while the PythonExpertAI class manages inference and fine-tuning operations. This approach allows for continuous model improvement while maintaining service availability through backup and rollback capabilities.

### Data Collection Pipeline
A **multi-source scraping architecture** collects training data from three primary sources:
- **Python Documentation Scraper**: Extracts content from official Python docs
- **GitHub Scraper**: Collects Python code examples and documentation from popular repositories  
- **Stack Overflow Scraper**: Gathers Q&A pairs from Python-related discussions

Each scraper implements rate limiting, content quality validation, and duplicate detection to ensure high-quality training data.

### Background Task Scheduling
The application uses **APScheduler** for automated task management with three main scheduled operations:
- Data collection (every 24 hours)
- Model training (every 72 hours)  
- Performance evaluation (daily at 2 AM)

This architecture ensures continuous system improvement without manual intervention while preventing resource conflicts through job isolation.

### Quality Control System
A comprehensive **quality scoring mechanism** evaluates content at multiple stages:
- Content length and structure validation
- Duplicate detection across sources
- Quality score calculation based on source credibility and content completeness
- Minimum thresholds for training data inclusion

This ensures only high-quality data contributes to model training, improving response accuracy.

## External Dependencies

### AI and Machine Learning
- **Hugging Face Transformers**: Provides the core language model infrastructure and tokenization
- **PyTorch**: Powers the underlying neural network computations and model training
- **Microsoft DialoGPT**: Serves as the base conversational AI model

### Web Technologies
- **Flask**: Core web framework for API and user interface
- **SQLAlchemy**: Database ORM for data modeling and queries
- **Bootstrap**: Frontend UI framework with dark theme support
- **Chart.js**: Data visualization for admin dashboard metrics

### Data Collection and Processing
- **Trafilatura**: Advanced web content extraction and cleaning
- **BeautifulSoup**: HTML parsing and content processing
- **Requests**: HTTP client for web scraping and API calls

### Task Scheduling and Background Processing
- **APScheduler**: Background task scheduling and job management
- **IntervalTrigger/CronTrigger**: Time-based task execution patterns

### API Integrations
- **GitHub API**: Repository content access and code example collection
- **Stack Overflow API**: Question and answer data retrieval for training
- **Python Documentation**: Official documentation scraping for authoritative content

### Development and Deployment
- **Werkzeug**: WSGI utilities and development server capabilities
- **Feather Icons**: Icon library for user interface elements
- **ProxyFix**: Handles reverse proxy headers for deployment scenarios