import logging
import time
from typing import List, Dict, Optional, Tuple
from ai_models.python_expert import PythonExpertAI
from data_processing.processor import DataProcessor
from models import UserQuery, ModelMetrics
from app import db
import statistics

logger = logging.getLogger(__name__)

# Try to import ML dependencies, fall back to simple evaluation if not available
try:
    import torch
    from transformers import Trainer, TrainingArguments
    ML_AVAILABLE = True
except ImportError as e:
    logger.warning(f"ML dependencies not available: {e}. Using simple evaluation.")
    ML_AVAILABLE = False

class ModelEvaluator:
    def __init__(self):
        self.data_processor = DataProcessor()
        
    def evaluate_model_performance(self, test_questions: List[str] = None) -> Dict:
        """
        Evaluate the current model's performance using test questions
        """
        logger.info("Starting model performance evaluation")
        
        if test_questions is None:
            test_questions = self._get_default_test_questions()
        
        try:
            # Load the AI model
            ai_model = PythonExpertAI()
            
            results = {
                'total_questions': len(test_questions),
                'successful_responses': 0,
                'failed_responses': 0,
                'average_response_time': 0.0,
                'quality_scores': [],
                'detailed_results': []
            }
            
            response_times = []
            quality_scores = []
            
            for i, question in enumerate(test_questions):
                try:
                    logger.info(f"Evaluating question {i+1}/{len(test_questions)}")
                    
                    # Generate response
                    start_time = time.time()
                    response, response_time = ai_model.generate_response(question)
                    end_time = time.time()
                    
                    actual_response_time = end_time - start_time
                    response_times.append(actual_response_time)
                    
                    if response and len(response.strip()) > 10:
                        # Evaluate response quality
                        quality_score = ai_model.evaluate_response_quality(question, response)
                        quality_scores.append(quality_score)
                        
                        results['successful_responses'] += 1
                        
                        # Store detailed result
                        results['detailed_results'].append({
                            'question': question,
                            'response': response,
                            'response_time': actual_response_time,
                            'quality_score': quality_score,
                            'success': True
                        })
                        
                        logger.debug(f"Question: {question[:50]}...")
                        logger.debug(f"Quality Score: {quality_score}")
                        
                    else:
                        results['failed_responses'] += 1
                        results['detailed_results'].append({
                            'question': question,
                            'response': response or "No response generated",
                            'response_time': actual_response_time,
                            'quality_score': 0.0,
                            'success': False
                        })
                        
                except Exception as e:
                    logger.error(f"Error evaluating question {i}: {str(e)}")
                    results['failed_responses'] += 1
                    results['detailed_results'].append({
                        'question': question,
                        'response': f"Error: {str(e)}",
                        'response_time': 0.0,
                        'quality_score': 0.0,
                        'success': False
                    })
            
            # Calculate summary statistics
            if response_times:
                results['average_response_time'] = statistics.mean(response_times)
                results['median_response_time'] = statistics.median(response_times)
                results['max_response_time'] = max(response_times)
                results['min_response_time'] = min(response_times)
            
            if quality_scores:
                results['average_quality_score'] = statistics.mean(quality_scores)
                results['median_quality_score'] = statistics.median(quality_scores)
                results['quality_scores'] = quality_scores
                results['quality_distribution'] = self._analyze_quality_distribution(quality_scores)
            
            results['success_rate'] = results['successful_responses'] / results['total_questions']
            
            logger.info(f"Evaluation completed: {results['successful_responses']}/{results['total_questions']} successful")
            return results
            
        except Exception as e:
            logger.error(f"Error during model evaluation: {str(e)}")
            return {'error': str(e)}
    
    def _get_default_test_questions(self) -> List[str]:
        """
        Get a set of default test questions for evaluation
        """
        return [
            "How do you create a list in Python?",
            "What is the difference between a list and a tuple in Python?",
            "How do you define a function in Python?",
            "What are Python decorators and how do you use them?",
            "How do you handle exceptions in Python?",
            "What is the difference between '==' and 'is' in Python?",
            "How do you read a file in Python?",
            "What are Python classes and how do you create them?",
            "How do you import modules in Python?",
            "What is list comprehension in Python?",
            "How do you iterate over a dictionary in Python?",
            "What are lambda functions in Python?",
            "How do you concatenate strings in Python?",
            "What is the difference between append() and extend() methods?",
            "How do you sort a list in Python?",
            "What are Python generators and how do they work?",
            "How do you work with JSON data in Python?",
            "What is the purpose of __init__ method in Python classes?",
            "How do you handle command line arguments in Python?",
            "What are Python virtual environments and why use them?"
        ]
    
    def _analyze_quality_distribution(self, quality_scores: List[float]) -> Dict:
        """
        Analyze the distribution of quality scores
        """
        if not quality_scores:
            return {}
        
        # Define quality ranges
        excellent = sum(1 for score in quality_scores if score >= 0.8)
        good = sum(1 for score in quality_scores if 0.6 <= score < 0.8)
        fair = sum(1 for score in quality_scores if 0.4 <= score < 0.6)
        poor = sum(1 for score in quality_scores if score < 0.4)
        
        total = len(quality_scores)
        
        return {
            'excellent': {'count': excellent, 'percentage': (excellent / total) * 100},
            'good': {'count': good, 'percentage': (good / total) * 100},
            'fair': {'count': fair, 'percentage': (fair / total) * 100},
            'poor': {'count': poor, 'percentage': (poor / total) * 100}
        }
    
    def evaluate_user_satisfaction(self, days_back: int = 30) -> Dict:
        """
        Evaluate user satisfaction based on ratings and usage patterns
        """
        try:
            from datetime import datetime, timedelta
            
            # Get user queries from the last N days
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            recent_queries = UserQuery.query.filter(
                UserQuery.created_at >= cutoff_date
            ).all()
            
            if not recent_queries:
                return {
                    'total_queries': 0,
                    'average_rating': 0.0,
                    'response_time_stats': {},
                    'rating_distribution': {}
                }
            
            # Calculate statistics
            total_queries = len(recent_queries)
            rated_queries = [q for q in recent_queries if q.user_rating is not None]
            response_times = [q.response_time for q in recent_queries if q.response_time is not None]
            
            results = {
                'total_queries': total_queries,
                'rated_queries': len(rated_queries),
                'days_analyzed': days_back
            }
            
            # Rating analysis
            if rated_queries:
                ratings = [q.user_rating for q in rated_queries]
                results['average_rating'] = statistics.mean(ratings)
                results['median_rating'] = statistics.median(ratings)
                
                # Rating distribution
                rating_counts = {}
                for rating in range(1, 6):
                    count = sum(1 for r in ratings if r == rating)
                    rating_counts[rating] = {
                        'count': count,
                        'percentage': (count / len(ratings)) * 100
                    }
                results['rating_distribution'] = rating_counts
                
                # Satisfaction metrics
                satisfied_count = sum(1 for r in ratings if r >= 4)
                results['satisfaction_rate'] = (satisfied_count / len(ratings)) * 100
            
            # Response time analysis
            if response_times:
                results['response_time_stats'] = {
                    'average': statistics.mean(response_times),
                    'median': statistics.median(response_times),
                    'min': min(response_times),
                    'max': max(response_times),
                    'fast_responses': sum(1 for t in response_times if t < 2.0),  # Under 2 seconds
                    'slow_responses': sum(1 for t in response_times if t > 10.0)  # Over 10 seconds
                }
            
            return results
            
        except Exception as e:
            logger.error(f"Error evaluating user satisfaction: {str(e)}")
            return {'error': str(e)}
    
    def generate_evaluation_report(self) -> Dict:
        """
        Generate a comprehensive evaluation report
        """
        logger.info("Generating comprehensive evaluation report")
        
        try:
            # Performance evaluation
            performance_results = self.evaluate_model_performance()
            
            # User satisfaction analysis
            satisfaction_results = self.evaluate_user_satisfaction()
            
            # Knowledge base statistics
            kb_stats = self.data_processor.get_knowledge_base_stats()
            
            # Recent model metrics
            from ai_models.model_manager import ModelManager
            model_manager = ModelManager()
            recent_metrics = model_manager.get_model_metrics(limit=5)
            current_model_info = model_manager.get_current_model_info()
            
            # Compile comprehensive report
            report = {
                'report_generated_at': time.time(),
                'model_performance': performance_results,
                'user_satisfaction': satisfaction_results,
                'knowledge_base_stats': kb_stats,
                'model_info': current_model_info,
                'recent_training_metrics': recent_metrics,
                'recommendations': self._generate_recommendations(
                    performance_results, satisfaction_results, kb_stats
                )
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating evaluation report: {str(e)}")
            return {'error': str(e)}
    
    def _generate_recommendations(self, performance: Dict, satisfaction: Dict, kb_stats: Dict) -> List[str]:
        """
        Generate recommendations based on evaluation results
        """
        recommendations = []
        
        # Performance-based recommendations
        if 'average_quality_score' in performance:
            if performance['average_quality_score'] < 0.6:
                recommendations.append("Model quality is below acceptable levels. Consider retraining with more high-quality data.")
            
            if performance['success_rate'] < 0.8:
                recommendations.append("Response success rate is low. Review error handling and model robustness.")
        
        # Response time recommendations
        if 'average_response_time' in performance:
            if performance['average_response_time'] > 5.0:
                recommendations.append("Response times are slow. Consider model optimization or hardware upgrades.")
        
        # User satisfaction recommendations
        if 'average_rating' in satisfaction:
            if satisfaction['average_rating'] < 3.5:
                recommendations.append("User satisfaction is low. Focus on improving response quality and relevance.")
        
        # Knowledge base recommendations
        if kb_stats.get('total_items', 0) < 1000:
            recommendations.append("Knowledge base is small. Increase data collection frequency.")
        
        unused_training_data = kb_stats.get('unused_training_data', 0)
        if unused_training_data > 500:
            recommendations.append(f"Large amount of unused training data ({unused_training_data} items). Consider scheduling model training.")
        
        # Data quality recommendations
        avg_quality = kb_stats.get('avg_quality_score', 0)
        if avg_quality < 0.7:
            recommendations.append("Average data quality is low. Review and improve data collection sources.")
        
        if not recommendations:
            recommendations.append("System performance is within acceptable parameters. Continue monitoring.")
        
        return recommendations
    
    def benchmark_against_baseline(self, baseline_questions: List[Dict] = None) -> Dict:
        """
        Benchmark current model against a baseline set of questions with expected answers
        """
        if baseline_questions is None:
            baseline_questions = self._get_baseline_qa_pairs()
        
        try:
            ai_model = PythonExpertAI()
            
            results = {
                'total_benchmarks': len(baseline_questions),
                'passed': 0,
                'failed': 0,
                'benchmark_score': 0.0,
                'detailed_results': []
            }
            
            for i, qa_pair in enumerate(baseline_questions):
                question = qa_pair['question']
                expected_keywords = qa_pair.get('expected_keywords', [])
                min_quality = qa_pair.get('min_quality', 0.5)
                
                try:
                    response, response_time = ai_model.generate_response(question)
                    quality_score = ai_model.evaluate_response_quality(question, response)
                    
                    # Check if response contains expected keywords
                    keyword_matches = 0
                    if expected_keywords:
                        for keyword in expected_keywords:
                            if keyword.lower() in response.lower():
                                keyword_matches += 1
                        keyword_score = keyword_matches / len(expected_keywords)
                    else:
                        keyword_score = 1.0  # No keywords to check
                    
                    # Overall benchmark score
                    benchmark_score = (quality_score * 0.7) + (keyword_score * 0.3)
                    
                    passed = benchmark_score >= min_quality
                    if passed:
                        results['passed'] += 1
                    else:
                        results['failed'] += 1
                    
                    results['detailed_results'].append({
                        'question': question,
                        'response': response,
                        'quality_score': quality_score,
                        'keyword_score': keyword_score,
                        'benchmark_score': benchmark_score,
                        'passed': passed,
                        'expected_keywords': expected_keywords,
                        'keyword_matches': keyword_matches
                    })
                    
                except Exception as e:
                    logger.error(f"Error in benchmark {i}: {str(e)}")
                    results['failed'] += 1
                    results['detailed_results'].append({
                        'question': question,
                        'error': str(e),
                        'passed': False
                    })
            
            results['benchmark_score'] = results['passed'] / results['total_benchmarks'] * 100
            
            return results
            
        except Exception as e:
            logger.error(f"Error during benchmarking: {str(e)}")
            return {'error': str(e)}
    
    def _get_baseline_qa_pairs(self) -> List[Dict]:
        """
        Get baseline Q&A pairs for benchmarking
        """
        return [
            {
                'question': 'How do you create a list in Python?',
                'expected_keywords': ['list', '[', ']', 'append'],
                'min_quality': 0.6
            },
            {
                'question': 'What is a Python function?',
                'expected_keywords': ['def', 'function', 'return', 'parameter'],
                'min_quality': 0.6
            },
            {
                'question': 'How do you handle exceptions in Python?',
                'expected_keywords': ['try', 'except', 'exception', 'finally'],
                'min_quality': 0.7
            },
            {
                'question': 'What are Python classes?',
                'expected_keywords': ['class', 'object', '__init__', 'method'],
                'min_quality': 0.6
            },
            {
                'question': 'How do you import modules in Python?',
                'expected_keywords': ['import', 'from', 'module', 'package'],
                'min_quality': 0.6
            }
        ]
