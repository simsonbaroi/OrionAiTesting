"""
Advanced Machine Learning Training System
Handles self-learning, model training, and continuous improvement
"""

import os
import json
import sqlite3
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MLTrainingSystem:
    """
    Advanced ML system for continuous learning and improvement
    """
    
    def __init__(self, db_path: str = "instance/ml_training.db"):
        self.db_path = db_path
        self.vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
        self.classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.initialize_ml_database()
        
    def initialize_ml_database(self):
        """Initialize ML training database"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Training samples table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS training_samples (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    input_text TEXT NOT NULL,
                    expected_output TEXT NOT NULL,
                    language TEXT NOT NULL,
                    category TEXT,
                    quality_score REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Model performance tracking
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS model_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_version TEXT NOT NULL,
                    accuracy REAL NOT NULL,
                    precision_score REAL,
                    recall_score REAL,
                    f1_score REAL,
                    training_samples_count INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Feature importance tracking
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS feature_importance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    feature_name TEXT NOT NULL,
                    importance_score REAL NOT NULL,
                    model_version TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    def add_training_sample(self, input_text: str, expected_output: str, 
                           language: str, category: str = None, quality_score: float = 1.0):
        """Add new training sample to the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO training_samples 
                (input_text, expected_output, language, category, quality_score)
                VALUES (?, ?, ?, ?, ?)
            ''', (input_text, expected_output, language, category, quality_score))
            conn.commit()
    
    def train_classification_model(self):
        """Train classification model on accumulated data"""
        try:
            # Load training data
            df = self.load_training_data()
            if len(df) < 10:
                logger.warning("Insufficient training data for ML training")
                return False
            
            # Prepare features and labels
            X = self.vectorizer.fit_transform(df['input_text'])
            y = df['category']
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Train model
            self.classifier.fit(X_train, y_train)
            
            # Evaluate model
            y_pred = self.classifier.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            # Store performance metrics
            model_version = f"v_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.store_model_performance(model_version, accuracy, len(df))
            
            # Store feature importance
            self.store_feature_importance(model_version)
            
            logger.info(f"Model training completed. Accuracy: {accuracy:.3f}")
            return True
            
        except Exception as e:
            logger.error(f"ML training failed: {str(e)}")
            return False
    
    def load_training_data(self) -> pd.DataFrame:
        """Load training data from database"""
        with sqlite3.connect(self.db_path) as conn:
            query = '''
                SELECT input_text, expected_output, language, category, quality_score
                FROM training_samples
                WHERE quality_score >= 0.5
                ORDER BY created_at DESC
            '''
            df = pd.read_sql_query(query, conn)
        return df
    
    def store_model_performance(self, version: str, accuracy: float, sample_count: int):
        """Store model performance metrics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO model_performance 
                (model_version, accuracy, training_samples_count)
                VALUES (?, ?, ?)
            ''', (version, accuracy, sample_count))
            conn.commit()
    
    def store_feature_importance(self, model_version: str):
        """Store feature importance scores"""
        try:
            feature_names = self.vectorizer.get_feature_names_out()
            importance_scores = self.classifier.feature_importances_
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                for feature, importance in zip(feature_names, importance_scores):
                    if importance > 0.001:  # Only store significant features
                        cursor.execute('''
                            INSERT INTO feature_importance 
                            (feature_name, importance_score, model_version)
                            VALUES (?, ?, ?)
                        ''', (feature, float(importance), model_version))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to store feature importance: {str(e)}")
    
    def predict_category(self, text: str) -> str:
        """Predict category for given text"""
        try:
            X = self.vectorizer.transform([text])
            prediction = self.classifier.predict(X)[0]
            probability = max(self.classifier.predict_proba(X)[0])
            
            if probability > 0.6:  # High confidence threshold
                return prediction
            else:
                return "uncertain"
        except Exception:
            return "unknown"
    
    def get_model_insights(self) -> dict:
        """Get insights about model performance and learning"""
        insights = {
            'total_samples': 0,
            'latest_accuracy': 0.0,
            'top_features': [],
            'performance_trend': []
        }
        
        with sqlite3.connect(self.db_path) as conn:
            # Get total samples
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM training_samples')
            insights['total_samples'] = cursor.fetchone()[0]
            
            # Get latest performance
            cursor.execute('''
                SELECT accuracy FROM model_performance 
                ORDER BY created_at DESC LIMIT 1
            ''')
            result = cursor.fetchone()
            if result:
                insights['latest_accuracy'] = result[0]
            
            # Get top features
            cursor.execute('''
                SELECT feature_name, importance_score 
                FROM feature_importance 
                ORDER BY importance_score DESC LIMIT 10
            ''')
            insights['top_features'] = [
                {'feature': row[0], 'importance': row[1]} 
                for row in cursor.fetchall()
            ]
            
            # Get performance trend
            cursor.execute('''
                SELECT accuracy, created_at 
                FROM model_performance 
                ORDER BY created_at DESC LIMIT 10
            ''')
            insights['performance_trend'] = [
                {'accuracy': row[0], 'date': row[1]} 
                for row in cursor.fetchall()
            ]
        
        return insights