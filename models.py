from app import db
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship


class KnowledgeBase(db.Model):
    """Store all collected knowledge and learning content"""
    __tablename__ = 'knowledge_base'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    source_type = Column(String(100), nullable=False)  # python_docs, stackoverflow, github, etc.
    source_url = Column(String(1000))
    language = Column(String(50), default='python')  # python, html, css, javascript, react
    difficulty = Column(String(20), default='intermediate')  # beginner, intermediate, advanced
    quality_score = Column(Float, default=0.0)
    tags = Column(JSON)  # ['functions', 'loops', 'oop']
    category = Column(String(100))  # syntax, data-structures, web-development, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    training_pairs = relationship("TrainingData", back_populates="knowledge_item")
    user_interactions = relationship("UserQuery", back_populates="related_knowledge")


class TrainingData(db.Model):
    """Q&A pairs generated from knowledge base for AI training"""
    __tablename__ = 'training_data'
    
    id = Column(Integer, primary_key=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    knowledge_base_id = Column(Integer, ForeignKey('knowledge_base.id'))
    language = Column(String(50), default='python')
    difficulty = Column(String(20), default='intermediate')
    question_type = Column(String(100))  # definition, example, debugging, best-practice
    quality_score = Column(Float, default=0.0)
    usage_count = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)  # How often this leads to good responses
    created_at = Column(DateTime, default=datetime.utcnow)
    is_validated = Column(Boolean, default=False)
    
    # Relationships
    knowledge_item = relationship("KnowledgeBase", back_populates="training_pairs")


class UserQuery(db.Model):
    """Store all user interactions and questions"""
    __tablename__ = 'user_queries'
    
    id = Column(Integer, primary_key=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    language = Column(String(50), default='python')
    session_id = Column(String(100))  # Track user sessions
    response_time = Column(Float)  # Time taken to generate response
    user_feedback = Column(String(20))  # positive, negative, neutral
    knowledge_base_id = Column(Integer, ForeignKey('knowledge_base.id'), nullable=True)
    answer_source = Column(String(100))  # knowledge_base, pattern_match, ai_generated
    context = Column(JSON)  # Store conversation context
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    related_knowledge = relationship("KnowledgeBase", back_populates="user_interactions")


class ModelMetrics(db.Model):
    """Track AI model performance and improvements"""
    __tablename__ = 'model_metrics'
    
    id = Column(Integer, primary_key=True)
    model_version = Column(String(50), nullable=False)
    language = Column(String(50), default='python')
    accuracy_score = Column(Float, default=0.0)
    response_quality = Column(Float, default=0.0)
    training_data_count = Column(Integer, default=0)
    knowledge_base_count = Column(Integer, default=0)
    user_satisfaction = Column(Float, default=0.0)
    evaluation_date = Column(DateTime, default=datetime.utcnow)
    metrics_data = Column(JSON)  # Store detailed metrics
    notes = Column(Text)


class ProjectTemplate(db.Model):
    """Store code templates and project structures"""
    __tablename__ = 'project_templates'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    language = Column(String(50), nullable=False)  # python, html, css, javascript, react
    category = Column(String(100))  # web-app, automation, data-analysis, etc.
    template_code = Column(Text, nullable=False)
    file_structure = Column(JSON)  # Directory and file structure
    dependencies = Column(JSON)  # Required packages/libraries
    instructions = Column(Text)  # Setup and usage instructions
    difficulty = Column(String(20), default='intermediate')
    popularity_score = Column(Float, default=0.0)
    usage_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_featured = Column(Boolean, default=False)


class CodeExample(db.Model):
    """Store specific code examples and snippets"""
    __tablename__ = 'code_examples'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(300), nullable=False)
    description = Column(Text)
    language = Column(String(50), nullable=False)
    category = Column(String(100))  # functions, classes, algorithms, ui-components
    code_snippet = Column(Text, nullable=False)
    explanation = Column(Text)
    input_example = Column(Text)
    output_example = Column(Text)
    related_concepts = Column(JSON)  # ['loops', 'conditionals']
    difficulty = Column(String(20), default='intermediate')
    knowledge_base_id = Column(Integer, ForeignKey('knowledge_base.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_tested = Column(Boolean, default=False)


class LearningPath(db.Model):
    """Define structured learning paths for different technologies"""
    __tablename__ = 'learning_paths'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    language = Column(String(50), nullable=False)
    target_audience = Column(String(100))  # beginner, intermediate, advanced
    estimated_duration = Column(String(50))  # "2 weeks", "1 month"
    curriculum = Column(JSON)  # Ordered list of topics and knowledge_base_ids
    prerequisites = Column(JSON)  # Required knowledge before starting
    learning_objectives = Column(JSON)  # What students will learn
    completion_criteria = Column(JSON)  # How to measure completion
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)


class UserProgress(db.Model):
    """Track individual user learning progress"""
    __tablename__ = 'user_progress'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(100), nullable=False)  # Session or user identifier
    learning_path_id = Column(Integer, ForeignKey('learning_paths.id'))
    current_topic = Column(String(200))
    completed_topics = Column(JSON)  # List of completed topic IDs
    quiz_scores = Column(JSON)  # Scores for different topics
    time_spent = Column(Integer, default=0)  # Minutes spent learning
    last_activity = Column(DateTime, default=datetime.utcnow)
    proficiency_level = Column(String(20), default='beginner')
    achievements = Column(JSON)  # Badges, milestones achieved
    notes = Column(Text)  # Personal notes or instructor feedback


class SystemConfig(db.Model):
    """Store system configuration and settings"""
    __tablename__ = 'system_config'
    
    id = Column(Integer, primary_key=True)
    config_key = Column(String(100), unique=True, nullable=False)
    config_value = Column(JSON, nullable=False)
    description = Column(Text)
    category = Column(String(50))  # ai_settings, data_collection, ui_preferences
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ScrapingLog(db.Model):
    """Log data collection and scraping activities"""
    __tablename__ = 'scraping_logs'
    
    id = Column(Integer, primary_key=True)
    source = Column(String(100), nullable=False)  # github, stackoverflow, python_docs
    url = Column(String(1000))
    status = Column(String(50), nullable=False)  # success, failed, partial
    items_collected = Column(Integer, default=0)
    error_message = Column(Text)
    execution_time = Column(Float)  # Time taken in seconds
    created_at = Column(DateTime, default=datetime.utcnow)
    scraping_metadata = Column(JSON)  # Additional scraping metadata