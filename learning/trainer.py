import logging
import os
from datetime import datetime
from typing import List, Dict, Optional
from ai_models.python_expert import PythonExpertAI
from ai_models.model_manager import ModelManager
from data_processing.processor import DataProcessor
from config import Config

logger = logging.getLogger(__name__)

# Try to import ML dependencies, fall back to simple training if not available
try:
    import torch
    from transformers import Trainer, TrainingArguments
    ML_AVAILABLE = True
except ImportError as e:
    logger.warning(f"ML dependencies not available: {e}. Using simple training.")
    ML_AVAILABLE = False

class ModelTrainer:
    def __init__(self):
        self.model_manager = ModelManager()
        self.data_processor = DataProcessor()
        self.config = Config()
        
    def train_model_with_new_data(self, force_training: bool = False) -> Dict:
        """
        Train the model with new collected data
        """
        logger.info("Starting model training process")
        
        results = {
            'success': False,
            'training_samples': 0,
            'model_version': None,
            'training_time': 0,
            'error': None
        }
        
        try:
            # Get available training data
            training_data = self.data_processor.get_training_data_for_model(
                limit=1000,
                min_quality=Config.MIN_QUALITY_SCORE
            )
            
            if not training_data:
                results['error'] = "No training data available"
                logger.warning("No training data available for training")
                return results
            
            if len(training_data) < Config.MIN_TRAINING_SAMPLES and not force_training:
                results['error'] = f"Insufficient training data: {len(training_data)} < {Config.MIN_TRAINING_SAMPLES}"
                logger.warning(f"Insufficient training data: {len(training_data)} samples")
                return results
            
            logger.info(f"Training with {len(training_data)} samples")
            
            # Create model version identifier
            model_version = datetime.now().strftime("%Y%m%d_%H%M%S")
            training_output_dir = f"./models/training_{model_version}"
            
            # Create backup of current model
            backup_success = self.model_manager.create_backup(model_version)
            if not backup_success:
                logger.warning("Failed to create model backup")
            
            # Load the current model
            ai_model = PythonExpertAI()
            
            # Check if we have a current model to load
            current_model_info = self.model_manager.get_current_model_info()
            if current_model_info:
                logger.info("Loading current model for fine-tuning")
                ai_model.load_model_from_path(self.model_manager.current_model_path)
            
            # Start training
            start_time = datetime.now()
            training_success = ai_model.fine_tune(training_data, training_output_dir)
            end_time = datetime.now()
            
            training_time = (end_time - start_time).total_seconds()
            
            if not training_success:
                results['error'] = "Model training failed"
                logger.error("Model training failed")
                return results
            
            # Evaluate the trained model
            evaluation_results = self.evaluate_trained_model(
                training_output_dir, training_data[:50]  # Use first 50 samples for evaluation
            )
            
            # Decide whether to promote the new model
            should_promote = self._should_promote_model(evaluation_results)
            
            if should_promote:
                # Promote the new model
                promote_success = self.model_manager.promote_model(training_output_dir, model_version)
                
                if promote_success:
                    # Mark training data as used
                    training_ids = [item['id'] for item in training_data if 'id' in item]
                    self.data_processor.mark_training_data_used(training_ids)
                    
                    # Save model metrics
                    self.model_manager.save_model_metrics(
                        model_version=model_version,
                        accuracy_score=evaluation_results.get('accuracy_score'),
                        loss=evaluation_results.get('loss'),
                        training_samples=len(training_data),
                        notes=f"Training completed successfully. Evaluation: {evaluation_results}"
                    )
                    
                    results['success'] = True
                    results['model_version'] = model_version
                    logger.info(f"Model training completed successfully. New model version: {model_version}")
                else:
                    results['error'] = "Failed to promote new model"
                    logger.error("Failed to promote new model")
            else:
                results['error'] = f"New model performance not satisfactory: {evaluation_results}"
                logger.warning(f"New model not promoted due to poor performance: {evaluation_results}")
            
            results['training_samples'] = len(training_data)
            results['training_time'] = training_time
            
            # Cleanup old backups
            self.model_manager.cleanup_old_backups(keep_count=5)
            
        except Exception as e:
            logger.error(f"Error during model training: {str(e)}")
            results['error'] = str(e)
        
        return results
    
    def evaluate_trained_model(self, model_path: str, test_data: List[Dict]) -> Dict:
        """
        Evaluate a trained model
        """
        logger.info(f"Evaluating model at {model_path}")
        
        try:
            # Load the model
            ai_model = PythonExpertAI()
            load_success = ai_model.load_model_from_path(model_path)
            
            if not load_success:
                logger.error("Failed to load model for evaluation")
                return {'error': 'Failed to load model'}
            
            total_score = 0.0
            response_times = []
            successful_responses = 0
            
            for i, item in enumerate(test_data):
                try:
                    question = item['question']
                    expected_answer = item['answer']
                    
                    # Generate response
                    response, response_time = ai_model.generate_response(question)
                    response_times.append(response_time)
                    
                    if response and len(response) > 10:
                        # Evaluate response quality
                        quality_score = ai_model.evaluate_response_quality(question, response)
                        total_score += quality_score
                        successful_responses += 1
                        
                        if i < 5:  # Log first few examples
                            logger.debug(f"Q: {question[:100]}...")
                            logger.debug(f"A: {response[:100]}...")
                            logger.debug(f"Quality: {quality_score}")
                    
                except Exception as e:
                    logger.error(f"Error evaluating item {i}: {str(e)}")
                    continue
            
            # Calculate metrics
            if successful_responses > 0:
                avg_quality = total_score / successful_responses
                avg_response_time = sum(response_times) / len(response_times)
                success_rate = successful_responses / len(test_data)
            else:
                avg_quality = 0.0
                avg_response_time = 0.0
                success_rate = 0.0
            
            evaluation_results = {
                'accuracy_score': avg_quality,
                'avg_response_time': avg_response_time,
                'success_rate': success_rate,
                'successful_responses': successful_responses,
                'total_tests': len(test_data)
            }
            
            logger.info(f"Evaluation completed: {evaluation_results}")
            return evaluation_results
            
        except Exception as e:
            logger.error(f"Error during model evaluation: {str(e)}")
            return {'error': str(e)}
    
    def _should_promote_model(self, evaluation_results: Dict) -> bool:
        """
        Decide whether to promote a new model based on evaluation results
        """
        if 'error' in evaluation_results:
            return False
        
        # Minimum thresholds for promotion
        min_accuracy = 0.4  # 40% minimum quality score
        min_success_rate = 0.7  # 70% successful responses
        
        accuracy = evaluation_results.get('accuracy_score', 0)
        success_rate = evaluation_results.get('success_rate', 0)
        
        # Check if model meets minimum requirements
        if accuracy < min_accuracy:
            logger.warning(f"Model accuracy too low: {accuracy} < {min_accuracy}")
            return False
        
        if success_rate < min_success_rate:
            logger.warning(f"Model success rate too low: {success_rate} < {min_success_rate}")
            return False
        
        # Compare with previous model if available
        previous_metrics = self.model_manager.get_model_metrics(limit=1)
        if previous_metrics:
            previous_accuracy = previous_metrics[0].get('accuracy_score', 0)
            
            # Only promote if significantly better (at least 5% improvement)
            improvement_threshold = 0.05
            if accuracy < previous_accuracy + improvement_threshold:
                logger.warning(f"Insufficient improvement: {accuracy} vs {previous_accuracy}")
                return False
        
        logger.info(f"Model promotion criteria met: accuracy={accuracy}, success_rate={success_rate}")
        return True
    
    def retrain_from_scratch(self, training_data: List[Dict]) -> Dict:
        """
        Retrain the model from scratch with all available data
        """
        logger.info("Starting complete model retraining")
        
        try:
            # Create new model version
            model_version = f"retrain_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            training_output_dir = f"./models/training_{model_version}"
            
            # Create fresh model instance
            ai_model = PythonExpertAI()
            
            # Start training
            start_time = datetime.now()
            training_success = ai_model.fine_tune(training_data, training_output_dir)
            end_time = datetime.now()
            
            if training_success:
                # Evaluate the model
                evaluation_results = self.evaluate_trained_model(
                    training_output_dir, training_data[:100]
                )
                
                # Promote the model
                self.model_manager.promote_model(training_output_dir, model_version)
                
                # Save metrics
                self.model_manager.save_model_metrics(
                    model_version=model_version,
                    accuracy_score=evaluation_results.get('accuracy_score'),
                    training_samples=len(training_data),
                    notes=f"Complete retraining. Evaluation: {evaluation_results}"
                )
                
                training_time = (end_time - start_time).total_seconds()
                
                return {
                    'success': True,
                    'model_version': model_version,
                    'training_samples': len(training_data),
                    'training_time': training_time,
                    'evaluation': evaluation_results
                }
            else:
                return {
                    'success': False,
                    'error': 'Training failed'
                }
                
        except Exception as e:
            logger.error(f"Error during complete retraining: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_training_status(self) -> Dict:
        """
        Get current training status and statistics
        """
        try:
            # Get available training data count
            available_data = self.data_processor.get_training_data_for_model(limit=1)
            total_available = len(self.data_processor.get_training_data_for_model(limit=10000))
            
            # Get model metrics
            recent_metrics = self.model_manager.get_model_metrics(limit=5)
            
            # Get current model info
            current_model = self.model_manager.get_current_model_info()
            
            # Get knowledge base stats
            kb_stats = self.data_processor.get_knowledge_base_stats()
            
            return {
                'current_model': current_model,
                'available_training_samples': total_available,
                'min_training_samples': Config.MIN_TRAINING_SAMPLES,
                'ready_for_training': total_available >= Config.MIN_TRAINING_SAMPLES,
                'recent_training_metrics': recent_metrics,
                'knowledge_base_stats': kb_stats
            }
            
        except Exception as e:
            logger.error(f"Error getting training status: {str(e)}")
            return {'error': str(e)}
