import os

class Config:
    """Configuration settings for PyLearnAI"""
    
    # Database settings
    DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///pylearn_ai.db")
    
    # Model settings
    MODEL_NAME = os.environ.get("MODEL_NAME", "microsoft/DialoGPT-medium")
    MODEL_CACHE_DIR = os.environ.get("MODEL_CACHE_DIR", "./model_cache")
    MAX_RESPONSE_LENGTH = int(os.environ.get("MAX_RESPONSE_LENGTH", "200"))
    
    # Training settings
    TRAINING_EPOCHS = int(os.environ.get("TRAINING_EPOCHS", "3"))
    TRAINING_BATCH_SIZE = int(os.environ.get("TRAINING_BATCH_SIZE", "4"))
    LEARNING_RATE = float(os.environ.get("LEARNING_RATE", "5e-5"))
    MIN_TRAINING_SAMPLES = int(os.environ.get("MIN_TRAINING_SAMPLES", "100"))
    
    # Scraping settings
    SCRAPING_DELAY = float(os.environ.get("SCRAPING_DELAY", "1.0"))
    MAX_PAGES_PER_SOURCE = int(os.environ.get("MAX_PAGES_PER_SOURCE", "50"))
    GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
    STACKOVERFLOW_KEY = os.environ.get("STACKOVERFLOW_KEY")
    
    # Quality thresholds
    MIN_QUALITY_SCORE = float(os.environ.get("MIN_QUALITY_SCORE", "0.5"))
    MIN_CONTENT_LENGTH = int(os.environ.get("MIN_CONTENT_LENGTH", "100"))
    
    # Scheduling settings
    DATA_COLLECTION_INTERVAL_HOURS = int(os.environ.get("DATA_COLLECTION_INTERVAL", "24"))  # hours
    MODEL_TRAINING_INTERVAL_HOURS = int(os.environ.get("MODEL_TRAINING_INTERVAL", "72"))   # hours
    
    # Flask settings
    SECRET_KEY = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
    DEBUG = os.environ.get("FLASK_DEBUG", "True").lower() == "true"