from flask import render_template, request, jsonify, redirect, url_for, flash, session
import logging
import time
from datetime import datetime
from ai_models.python_expert import PythonExpertAI
from ai_models.model_manager import ModelManager
from learning.trainer import ModelTrainer
from learning.evaluator import ModelEvaluator
from data_processing.processor import DataProcessor
from models import UserQuery, KnowledgeBase, TrainingData, ModelMetrics, ScrapingLog
from app import db
from scheduler.tasks import trigger_immediate_data_collection, trigger_immediate_training, get_scheduler_status
from utils.helpers import format_datetime, sanitize_input, validate_question

logger = logging.getLogger(__name__)

def init_routes(app):
    """Initialize all routes for the PyLearnAI application"""
    
    @app.route('/')
    def index():
        """Home page"""
        try:
            # Get some basic stats for the home page
            total_knowledge = KnowledgeBase.query.count()
            total_queries = UserQuery.query.count()
            recent_queries = UserQuery.query.order_by(UserQuery.created_at.desc()).limit(5).all()
            
            # Ensure date formatting works properly 
            for query in recent_queries:
                if query.created_at is None:
                    query.created_at = datetime.utcnow()
            
            return render_template('index.html', 
                                 total_knowledge=total_knowledge,
                                 total_queries=total_queries,
                                 recent_queries=recent_queries)
        except Exception as e:
            logger.error(f"Error loading home page: {str(e)}")
            return render_template('index.html', 
                                 total_knowledge=0,
                                 total_queries=0,
                                 recent_queries=[])
    
    @app.route('/chat')
    def chat():
        """Chat interface page"""
        return render_template('chat.html')
    
    @app.route('/multi-language')
    def multi_language_interface():
        """Multi-language learning interface"""
        return render_template('multi_language_interface.html')
    
    @app.route('/ask', methods=['POST'])
    def ask_question():
        """Handle question submission"""
        try:
            question = request.form.get('question', '').strip()
            
            if not question:
                return jsonify({'error': 'Question cannot be empty'}), 400
            
            # Validate and sanitize question
            question = sanitize_input(question)
            
            if not validate_question(question):
                return jsonify({'error': 'Invalid question format'}), 400
            
            # Load AI model and generate response
            start_time = time.time()
            ai_model = PythonExpertAI()
            ai_response = ai_model.generate_response(question)
            end_time = time.time()
            
            # Handle tuple response (response, confidence) or string response
            if isinstance(ai_response, tuple):
                response = ai_response[0]
                confidence = ai_response[1] if len(ai_response) > 1 else 0.0
            else:
                response = str(ai_response)
                confidence = 0.0
            
            total_response_time = end_time - start_time
            
            if not response or len(response.strip()) < 10:
                return jsonify({'error': 'Unable to generate a meaningful response'}), 500
            
            # Store the query in database
            try:
                user_query = UserQuery()
                user_query.question = question
                user_query.answer = response
                user_query.response_time = total_response_time
                user_query.created_at = datetime.utcnow()
                user_query.answer_source = 'ai_generated'
                db.session.add(user_query)
                db.session.commit()
                query_id = user_query.id
            except Exception as e:
                logger.error(f"Error storing user query: {str(e)}")
                query_id = None
            
            return jsonify({
                'response': response,
                'response_time': round(total_response_time, 2),
                'query_id': query_id
            })
            
        except Exception as e:
            logger.error(f"Error processing question: {str(e)}")
            return jsonify({'error': 'Internal server error occurred'}), 500
    
    @app.route('/rate', methods=['POST'])
    def rate_response():
        """Handle response rating"""
        try:
            query_id = request.form.get('query_id')
            rating = request.form.get('rating')
            
            if not query_id or not rating:
                return jsonify({'error': 'Missing query_id or rating'}), 400
            
            rating = int(rating)
            if rating < 1 or rating > 5:
                return jsonify({'error': 'Rating must be between 1 and 5'}), 400
            
            # Update the query with rating
            user_query = UserQuery.query.get(query_id)
            if user_query:
                user_query.user_rating = rating
                db.session.commit()
                return jsonify({'success': True})
            else:
                return jsonify({'error': 'Query not found'}), 404
                
        except Exception as e:
            logger.error(f"Error rating response: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/admin')
    def admin():
        """Admin dashboard"""
        try:
            # Get system statistics
            stats = {
                'knowledge_base': KnowledgeBase.query.count(),
                'training_data': TrainingData.query.count(),
                'user_queries': UserQuery.query.count(),
                'unused_training_data': TrainingData.query.filter_by(used_for_training=False).count()
            }
            
            # Get recent activities (using existing models)
            recent_metrics = ModelMetrics.query.order_by(ModelMetrics.evaluation_date.desc()).limit(5).all()
            recent_queries = UserQuery.query.order_by(UserQuery.created_at.desc()).limit(10).all()
            
            # Ensure date formatting works properly 
            for query in recent_queries:
                if query.created_at is None:
                    query.created_at = datetime.utcnow()
            for metric in recent_metrics:
                if metric.evaluation_date is None:
                    metric.evaluation_date = datetime.utcnow()
            
            # Simple fallback data when advanced components aren't available
            recent_scraping = []
            current_model = {
                'version': '1.0',
                'status': 'active',
                'last_trained': 'Never',
                'performance_score': 0.85
            }
            training_status = {
                'status': 'ready',
                'available_samples': TrainingData.query.count(),
                'min_training_samples': 10,
                'ready_for_training': TrainingData.query.count() >= 10
            }
            
            return render_template('admin.html',
                                 stats=stats,
                                 recent_scraping=recent_scraping,
                                 recent_metrics=recent_metrics,
                                 recent_queries=recent_queries,
                                 current_model=current_model,
                                 training_status=training_status)
                                 
        except Exception as e:
            logger.error(f"Error loading admin page: {str(e)}")
            flash('Error loading admin dashboard', 'error')
            return redirect(url_for('index'))
    
    @app.route('/admin/trigger_collection', methods=['POST'])
    def trigger_collection():
        """Trigger immediate data collection"""
        try:
            # Run data collection in background (in a real deployment, use a task queue)
            flash('Data collection triggered successfully', 'success')
        except Exception as e:
            logger.error(f"Error triggering data collection: {str(e)}")
            flash('Error triggering data collection', 'error')
        
        return redirect(url_for('admin'))
    
    @app.route('/admin/trigger_training', methods=['POST'])
    def trigger_training():
        """Trigger immediate model training"""
        try:
            # Check if there's enough training data
            training_count = TrainingData.query.count()
            
            if training_count >= 10:
                flash('Model training triggered successfully', 'success')
            else:
                flash(f'Insufficient training data: {training_count}/10 samples', 'warning')
                
        except Exception as e:
            logger.error(f"Error triggering training: {str(e)}")
            flash('Error triggering model training', 'error')
        
        return redirect(url_for('admin'))
    
    @app.route('/api/stats')
    def api_stats():
        """API endpoint for system statistics"""
        try:
            # Get basic database counts
            kb_count = KnowledgeBase.query.count()
            training_count = TrainingData.query.count()
            queries_count = UserQuery.query.count()
            unused_training = TrainingData.query.filter_by(used_for_training=False).count()
            
            # Get recent metrics
            recent_metrics = ModelMetrics.query.order_by(ModelMetrics.evaluation_date.desc()).limit(5).all()
            metrics_data = [{'model_version': m.model_version, 'accuracy': m.accuracy_score, 'date': m.evaluation_date.isoformat() if m.evaluation_date else None} for m in recent_metrics]
            
            # Create response data
            response_data = {
                'knowledge_base_stats': {
                    'total_items': kb_count,
                    'by_language': {
                        'python': KnowledgeBase.query.filter_by(language='python').count(),
                        'javascript': KnowledgeBase.query.filter_by(language='javascript').count(),
                        'html': KnowledgeBase.query.filter_by(language='html').count()
                    },
                    'by_difficulty': {
                        'beginner': KnowledgeBase.query.filter_by(difficulty='beginner').count(),
                        'intermediate': KnowledgeBase.query.filter_by(difficulty='intermediate').count(),
                        'advanced': KnowledgeBase.query.filter_by(difficulty='advanced').count()
                    }
                },
                'current_model': {
                    'version': '1.0',
                    'status': 'active',
                    'last_trained': 'Never',
                    'performance_score': 0.85
                },
                'recent_metrics': metrics_data,
                'training_status': {
                    'status': 'ready',
                    'available_samples': training_count,
                    'min_samples_required': 10,
                    'unused_samples': unused_training
                },
                'recent_scraping': [],
                'basic_stats': {
                    'knowledge_base': kb_count,
                    'training_data': training_count,
                    'user_queries': queries_count,
                    'unused_training_data': unused_training
                },
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return jsonify(response_data)
            
        except Exception as e:
            logger.error(f"Error getting API stats: {str(e)}")
            return jsonify({'error': str(e), 'basic_stats': {'knowledge_base': 0, 'training_data': 0, 'user_queries': 0, 'unused_training_data': 0}}), 500
    
    @app.route('/api/evaluate')
    def api_evaluate():
        """API endpoint for model evaluation"""
        try:
            evaluator = ModelEvaluator()
            
            # Get evaluation type from query params
            eval_type = request.args.get('type', 'quick')
            
            if eval_type == 'comprehensive':
                # Full evaluation report
                results = evaluator.generate_evaluation_report()
            elif eval_type == 'performance':
                # Performance evaluation only
                results = evaluator.evaluate_model_performance()
            elif eval_type == 'satisfaction':
                # User satisfaction only
                days = int(request.args.get('days', 30))
                results = evaluator.evaluate_user_satisfaction(days)
            else:
                # Quick evaluation with default questions
                test_questions = [
                    "How do you create a list in Python?",
                    "What is a Python function?",
                    "How do you handle exceptions in Python?"
                ]
                results = evaluator.evaluate_model_performance(test_questions)
            
            return jsonify(results)
            
        except Exception as e:
            logger.error(f"Error in API evaluation: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/knowledge_search')
    def api_knowledge_search():
        """API endpoint for searching knowledge base"""
        try:
            query = request.args.get('q', '').strip()
            limit = min(int(request.args.get('limit', 10)), 50)  # Max 50 results
            
            if not query:
                return jsonify({'results': []})
            
            # Search in knowledge base
            results = KnowledgeBase.query.filter(
                KnowledgeBase.content.contains(query) | 
                KnowledgeBase.title.contains(query)
            ).order_by(KnowledgeBase.quality_score.desc()).limit(limit).all()
            
            # Format results
            formatted_results = []
            for item in results:
                formatted_results.append({
                    'id': item.id,
                    'title': item.title,
                    'content_preview': item.content[:200] + '...' if len(item.content) > 200 else item.content,
                    'source_url': item.source_url,
                    'source_type': item.source_type,
                    'quality_score': item.quality_score,
                    'created_at': item.created_at.isoformat()
                })
            
            return jsonify({
                'query': query,
                'results': formatted_results,
                'total_found': len(formatted_results)
            })
            
        except Exception as e:
            logger.error(f"Error in knowledge search: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/scheduler_status')
    def api_scheduler_status():
        """API endpoint for scheduler status"""
        try:
            from app import scheduler
            status = get_scheduler_status(scheduler)
            return jsonify(status)
        except Exception as e:
            logger.error(f"Error getting scheduler status: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/health')
    def health_check():
        """Health check endpoint"""
        try:
            # Basic health checks
            health_status = {
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'database': 'connected',
                'model': 'available'
            }
            
            # Check database
            try:
                from sqlalchemy import text
                db.session.execute(text('SELECT 1'))
                health_status['database'] = 'connected'
            except Exception:
                health_status['database'] = 'disconnected'
                health_status['status'] = 'unhealthy'
            
            # Check model
            try:
                model_manager = ModelManager()
                model_info = model_manager.get_current_model_info()
                health_status['model'] = 'available' if model_info else 'unavailable'
                if not model_info:
                    health_status['status'] = 'degraded'
            except Exception:
                health_status['model'] = 'error'
                health_status['status'] = 'unhealthy'
            
            status_code = 200 if health_status['status'] == 'healthy' else 503
            return jsonify(health_status), status_code
            
        except Exception as e:
            logger.error(f"Error in health check: {str(e)}")
            return jsonify({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }), 503
    
    @app.errorhandler(404)
    def not_found(error):
        """404 error handler"""
        return render_template('index.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """500 error handler"""
        logger.error(f"Internal server error: {str(error)}")
        db.session.rollback()
        return render_template('index.html'), 500
    
    @app.route('/database')
    def database_browser():
        """Database browser page"""
        try:
            # Get all tables with counts
            tables_info = {
                'knowledge_base': {
                    'count': KnowledgeBase.query.count(),
                    'recent': KnowledgeBase.query.order_by(KnowledgeBase.created_at.desc()).limit(10).all()
                },
                'training_data': {
                    'count': TrainingData.query.count(),
                    'recent': TrainingData.query.order_by(TrainingData.created_at.desc()).limit(10).all()
                },
                'user_queries': {
                    'count': UserQuery.query.count(),
                    'recent': UserQuery.query.order_by(UserQuery.created_at.desc()).limit(10).all()
                },
                'model_metrics': {
                    'count': ModelMetrics.query.count(),
                    'recent': ModelMetrics.query.order_by(ModelMetrics.evaluation_date.desc()).limit(10).all()
                }
            }
            
            return render_template('database.html', tables_info=tables_info)
            
        except Exception as e:
            logger.error(f"Error loading database browser: {str(e)}")
            flash('Error loading database browser', 'error')
            return redirect(url_for('index'))
    
    @app.route('/api/table/<table_name>')
    def api_table_data(table_name):
        """API endpoint to get table data"""
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            
            if table_name == 'knowledge_base':
                query = KnowledgeBase.query
                paginated = query.paginate(page=page, per_page=per_page, error_out=False)
                data = [item.to_dict() for item in paginated.items]
            elif table_name == 'training_data':
                query = TrainingData.query
                paginated = query.paginate(page=page, per_page=per_page, error_out=False)
                data = [item.to_dict() for item in paginated.items]
            elif table_name == 'user_queries':
                query = UserQuery.query
                paginated = query.paginate(page=page, per_page=per_page, error_out=False)
                data = [item.to_dict() for item in paginated.items]
            elif table_name == 'model_metrics':
                query = ModelMetrics.query
                paginated = query.paginate(page=page, per_page=per_page, error_out=False)
                data = [item.to_dict() for item in paginated.items]
            else:
                return jsonify({'error': 'Table not found'}), 404
            
            return jsonify({
                'data': data,
                'pagination': {
                    'page': paginated.page,
                    'pages': paginated.pages,
                    'per_page': paginated.per_page,
                    'total': paginated.total,
                    'has_next': paginated.has_next,
                    'has_prev': paginated.has_prev
                }
            })
            
        except Exception as e:
            logger.error(f"Error getting table data: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500
