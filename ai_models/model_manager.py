import os
import shutil
from datetime import datetime
import logging
from models import ModelMetrics
from app import db

logger = logging.getLogger(__name__)

class ModelManager:
    def __init__(self, base_model_dir="./models"):
        self.base_model_dir = base_model_dir
        self.current_model_path = os.path.join(base_model_dir, "current")
        self.backup_model_dir = os.path.join(base_model_dir, "backups")
        
        # Create directories if they don't exist
        os.makedirs(base_model_dir, exist_ok=True)
        os.makedirs(self.backup_model_dir, exist_ok=True)
    
    def create_backup(self, model_version=None):
        """Create a backup of the current model"""
        try:
            if not os.path.exists(self.current_model_path):
                logger.warning("No current model to backup")
                return False
            
            if model_version is None:
                model_version = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            backup_path = os.path.join(self.backup_model_dir, f"model_{model_version}")
            
            # Copy current model to backup
            shutil.copytree(self.current_model_path, backup_path)
            logger.info(f"Model backup created at {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating backup: {str(e)}")
            return False
    
    def restore_backup(self, model_version):
        """Restore a model from backup"""
        try:
            backup_path = os.path.join(self.backup_model_dir, f"model_{model_version}")
            
            if not os.path.exists(backup_path):
                logger.error(f"Backup model {model_version} not found")
                return False
            
            # Remove current model
            if os.path.exists(self.current_model_path):
                shutil.rmtree(self.current_model_path)
            
            # Copy backup to current
            shutil.copytree(backup_path, self.current_model_path)
            logger.info(f"Model restored from backup {model_version}")
            return True
            
        except Exception as e:
            logger.error(f"Error restoring backup: {str(e)}")
            return False
    
    def promote_model(self, new_model_path, model_version=None):
        """Promote a newly trained model to current"""
        try:
            # Create backup of current model first
            if os.path.exists(self.current_model_path):
                self.create_backup(model_version)
                shutil.rmtree(self.current_model_path)
            
            # Copy new model to current
            shutil.copytree(new_model_path, self.current_model_path)
            logger.info(f"New model promoted to current from {new_model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error promoting model: {str(e)}")
            return False
    
    def list_backups(self):
        """List all available model backups"""
        try:
            backups = []
            if os.path.exists(self.backup_model_dir):
                for item in os.listdir(self.backup_model_dir):
                    if item.startswith("model_"):
                        version = item.replace("model_", "")
                        path = os.path.join(self.backup_model_dir, item)
                        created_time = os.path.getctime(path)
                        backups.append({
                            'version': version,
                            'path': path,
                            'created_at': datetime.fromtimestamp(created_time)
                        })
            
            return sorted(backups, key=lambda x: x['created_at'], reverse=True)
            
        except Exception as e:
            logger.error(f"Error listing backups: {str(e)}")
            return []
    
    def cleanup_old_backups(self, keep_count=5):
        """Remove old backups, keeping only the specified number"""
        try:
            backups = self.list_backups()
            
            if len(backups) > keep_count:
                for backup in backups[keep_count:]:
                    shutil.rmtree(backup['path'])
                    logger.info(f"Removed old backup: {backup['version']}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error cleaning up backups: {str(e)}")
            return False
    
    def save_model_metrics(self, model_version, accuracy_score=None, loss=None, training_samples=None, notes=None):
        """Save model evaluation metrics to database"""
        try:
            metrics = ModelMetrics(
                model_version=model_version,
                accuracy_score=accuracy_score,
                loss=loss,
                training_samples=training_samples,
                notes=notes
            )
            
            db.session.add(metrics)
            db.session.commit()
            logger.info(f"Model metrics saved for version {model_version}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving model metrics: {str(e)}")
            db.session.rollback()
            return False
    
    def get_model_metrics(self, limit=10):
        """Get recent model metrics"""
        try:
            metrics = ModelMetrics.query.order_by(ModelMetrics.evaluation_date.desc()).limit(limit).all()
            return [metric.to_dict() for metric in metrics]
        except Exception as e:
            logger.error(f"Error getting model metrics: {str(e)}")
            return []
    
    def get_current_model_info(self):
        """Get information about the current model"""
        try:
            if not os.path.exists(self.current_model_path):
                return None
            
            # Get model directory stats
            created_time = os.path.getctime(self.current_model_path)
            modified_time = os.path.getmtime(self.current_model_path)
            
            # Calculate directory size
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(self.current_model_path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    total_size += os.path.getsize(filepath)
            
            return {
                'path': self.current_model_path,
                'created_at': datetime.fromtimestamp(created_time),
                'modified_at': datetime.fromtimestamp(modified_time),
                'size_mb': round(total_size / (1024 * 1024), 2)
            }
            
        except Exception as e:
            logger.error(f"Error getting current model info: {str(e)}")
            return None
