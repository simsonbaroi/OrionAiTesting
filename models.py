from app import db
from datetime import datetime
import json

class KnowledgeBase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    content = db.Column(db.Text, nullable=False)
    source_url = db.Column(db.String(1000))
    source_type = db.Column(db.String(50))  # 'python_docs', 'stackoverflow', 'github'
    quality_score = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'source_url': self.source_url,
            'source_type': self.source_type,
            'quality_score': self.quality_score,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class TrainingData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    source = db.Column(db.String(100))
    quality_score = db.Column(db.Float, default=0.0)
    used_for_training = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'question': self.question,
            'answer': self.answer,
            'source': self.source,
            'quality_score': self.quality_score,
            'used_for_training': self.used_for_training,
            'created_at': self.created_at.isoformat()
        }

class ModelMetrics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    model_version = db.Column(db.String(50), nullable=False)
    accuracy_score = db.Column(db.Float)
    loss = db.Column(db.Float)
    training_samples = db.Column(db.Integer)
    evaluation_date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'model_version': self.model_version,
            'accuracy_score': self.accuracy_score,
            'loss': self.loss,
            'training_samples': self.training_samples,
            'evaluation_date': self.evaluation_date.isoformat(),
            'notes': self.notes
        }

class ScrapingLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source_type = db.Column(db.String(50), nullable=False)
    urls_scraped = db.Column(db.Integer, default=0)
    items_collected = db.Column(db.Integer, default=0)
    errors_count = db.Column(db.Integer, default=0)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='running')  # 'running', 'completed', 'failed'
    error_details = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'source_type': self.source_type,
            'urls_scraped': self.urls_scraped,
            'items_collected': self.items_collected,
            'errors_count': self.errors_count,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'status': self.status,
            'error_details': self.error_details
        }

class UserQueries(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text)
    response_time = db.Column(db.Float)  # in seconds
    user_rating = db.Column(db.Integer)  # 1-5 rating
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'question': self.question,
            'answer': self.answer,
            'response_time': self.response_time,
            'user_rating': self.user_rating,
            'created_at': self.created_at.isoformat()
        }
