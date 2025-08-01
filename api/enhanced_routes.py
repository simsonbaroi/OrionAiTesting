"""
Enhanced Routes with Integrated AI System
Provides comprehensive programming assistance across all languages and frameworks
"""

from flask import render_template, request, jsonify, session
import logging
import time
import json
from datetime import datetime
from typing import Dict, Any

# Import the integrated AI system
from ai_models.integrated_ai_system import integrated_ai
from models import UserQuery, KnowledgeBase, TrainingData, ModelMetrics
from app import db
from utils.helpers import format_datetime, sanitize_input, validate_question

logger = logging.getLogger(__name__)

def init_enhanced_routes(app):
    """Initialize enhanced routes with comprehensive AI capabilities"""
    
    @app.route('/api/enhanced-ask', methods=['POST'])
    def enhanced_ask_question():
        """Enhanced question handling with multi-model AI system"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No JSON data provided'}), 400
            
            question = data.get('question', '').strip()
            language = data.get('language', '').strip()
            context = data.get('context', '').strip()
            request_type = data.get('request_type', 'general').strip()
            use_both_models = data.get('use_both_models', False)
            
            if not question:
                return jsonify({'error': 'Question cannot be empty'}), 400
            
            # Validate and sanitize inputs
            question = sanitize_input(question)
            language = sanitize_input(language) if language else None
            context = sanitize_input(context) if context else ""
            
            if not validate_question(question):
                return jsonify({'error': 'Invalid question format'}), 400
            
            # Process with multi-model AI system if available
            start_time = time.time()
            
            if integrated_ai.components['multi_model_ai']:
                import asyncio
                ai_response = asyncio.run(integrated_ai.multi_model_ai.generate_enhanced_response(
                    query=question,
                    language=language or 'general',
                    context=context,
                    task_type=request_type,
                    use_both_models=use_both_models
                ))
            else:
                # Fallback to integrated AI system
                ai_response = integrated_ai.process_query(
                    query=question,
                    language=language,
                    context=context,
                    request_type=request_type
                )
            
            end_time = time.time()
            total_response_time = end_time - start_time
            
            # Store the query in database
            try:
                user_query = UserQuery()
                user_query.question = question
                user_query.answer = ai_response.get('response', 'No response generated')
                user_query.response_time = total_response_time
                user_query.language = language or 'general'
                user_query.context = context
                db.session.add(user_query)
                db.session.commit()
                query_id = user_query.id
            except Exception as e:
                logger.error(f"Error storing user query: {str(e)}")
                query_id = None
            
            # Enhanced response with multi-model data
            response_data = {
                'success': ai_response.get('success', True),
                'response': ai_response.get('response', ''),
                'component_used': ai_response.get('model_used', ai_response.get('component_used', 'unknown')),
                'language': ai_response.get('language', language),
                'response_time': round(total_response_time, 2),
                'query_id': query_id
            }
            
            # Add multi-model specific data
            if 'response_type' in ai_response and ai_response['response_type'] == 'comparison':
                response_data.update({
                    'comparison_mode': True,
                    'openai_response': ai_response.get('openai_response'),
                    'deepseek_response': ai_response.get('deepseek_response'),
                    'primary_model': ai_response.get('primary_model'),
                    'openai_tokens': ai_response.get('openai_tokens', 0),
                    'deepseek_tokens': ai_response.get('deepseek_tokens', 0)
                })
            else:
                response_data.update({
                    'tokens_used': ai_response.get('tokens_used', 0),
                    'quality_score': ai_response.get('quality_score', 0.8),
                    'capabilities': ai_response.get('capabilities', []),
                    'enhancements': ai_response.get('enhancements', {})
                })
            
            return jsonify(response_data)
            
        except Exception as e:
            logger.error(f"Error in enhanced question processing: {str(e)}")
            return jsonify({'error': 'Internal server error occurred'}), 500
    
    @app.route('/api/generate-code', methods=['POST'])
    def generate_code():
        """Generate code with comprehensive AI support"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No JSON data provided'}), 400
            
            description = data.get('description', '').strip()
            language = data.get('language', '').strip()
            complexity = data.get('complexity', 'intermediate').strip()
            include_tests = data.get('include_tests', True)
            
            if not description or not language:
                return jsonify({'error': 'Description and language are required'}), 400
            
            # Sanitize inputs
            description = sanitize_input(description)
            language = sanitize_input(language)
            
            # Generate code with full AI support
            start_time = time.time()
            result = integrated_ai.generate_code_with_full_support(
                description=description,
                language=language,
                complexity=complexity,
                include_tests=include_tests
            )
            end_time = time.time()
            
            result['generation_time'] = round(end_time - start_time, 2)
            
            return jsonify({
                'success': True,
                **result
            })
            
        except Exception as e:
            logger.error(f"Error in code generation: {str(e)}")
            return jsonify({'error': 'Code generation failed'}), 500
    
    @app.route('/api/debug-code', methods=['POST'])
    def debug_code():
        """Comprehensive code debugging assistance"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No JSON data provided'}), 400
            
            code = data.get('code', '').strip()
            error_message = data.get('error_message', '').strip()
            language = data.get('language', '').strip()
            context = data.get('context', '').strip()
            
            if not code or not error_message or not language:
                return jsonify({'error': 'Code, error message, and language are required'}), 400
            
            # Sanitize inputs
            code = sanitize_input(code)
            error_message = sanitize_input(error_message)
            language = sanitize_input(language)
            context = sanitize_input(context) if context else ""
            
            # Get comprehensive debugging assistance
            start_time = time.time()
            debug_result = integrated_ai.comprehensive_debug_assistance(
                code=code,
                error_message=error_message,
                language=language,
                context=context
            )
            end_time = time.time()
            
            debug_result['debug_time'] = round(end_time - start_time, 2)
            
            return jsonify({
                'success': True,
                **debug_result
            })
            
        except Exception as e:
            logger.error(f"Error in code debugging: {str(e)}")
            return jsonify({'error': 'Code debugging failed'}), 500
    
    @app.route('/api/analyze-code', methods=['POST'])
    def analyze_code():
        """Analyze code for patterns, issues, and improvements"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No JSON data provided'}), 400
            
            code = data.get('code', '').strip()
            language = data.get('language', '').strip()
            context = data.get('context', '').strip()
            
            if not code or not language:
                return jsonify({'error': 'Code and language are required'}), 400
            
            # Sanitize inputs
            code = sanitize_input(code)
            language = sanitize_input(language)
            context = sanitize_input(context) if context else ""
            
            # Analyze code with enhanced AI
            start_time = time.time()
            analysis = integrated_ai.enhanced_ai.analyze_code(code, language, context)
            end_time = time.time()
            
            analysis['analysis_time'] = round(end_time - start_time, 2)
            
            return jsonify({
                'success': True,
                'analysis': analysis
            })
            
        except Exception as e:
            logger.error(f"Error in code analysis: {str(e)}")
            return jsonify({'error': 'Code analysis failed'}), 500
    
    @app.route('/api/get-suggestions', methods=['POST'])
    def get_code_suggestions():
        """Get intelligent code suggestions"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No JSON data provided'}), 400
            
            partial_code = data.get('partial_code', '').strip()
            language = data.get('language', '').strip()
            context = data.get('context', '').strip()
            
            if not language:
                return jsonify({'error': 'Language is required'}), 400
            
            # Sanitize inputs
            partial_code = sanitize_input(partial_code) if partial_code else ""
            language = sanitize_input(language)
            context = sanitize_input(context) if context else ""
            
            # Get smart suggestions
            suggestions = integrated_ai.enhanced_ai.get_smart_suggestions(
                partial_code=partial_code,
                language=language,
                context=context
            )
            
            return jsonify({
                'success': True,
                'suggestions': suggestions,
                'language': language
            })
            
        except Exception as e:
            logger.error(f"Error getting suggestions: {str(e)}")
            return jsonify({'error': 'Failed to get suggestions'}), 500
    
    @app.route('/api/learn-concept', methods=['POST'])
    def learn_programming_concept():
        """Learn programming concepts with AI assistance"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No JSON data provided'}), 400
            
            concept = data.get('concept', '').strip()
            language = data.get('language', '').strip()
            experience_level = data.get('experience_level', 'intermediate').strip()
            
            if not concept or not language:
                return jsonify({'error': 'Concept and language are required'}), 400
            
            # Sanitize inputs
            concept = sanitize_input(concept)
            language = sanitize_input(language)
            experience_level = sanitize_input(experience_level)
            
            # Get comprehensive learning assistance
            start_time = time.time()
            if integrated_ai.components['openai_enhanced']:
                learning_result = integrated_ai.openai_ai.learn_programming_concept(
                    concept=concept,
                    language=language,
                    experience_level=experience_level
                )
            else:
                learning_result = {
                    'learning_content': f"Learning concept '{concept}' in {language} for {experience_level} level. Please refer to official documentation for detailed information.",
                    'concept': concept,
                    'language': language,
                    'experience_level': experience_level,
                    'estimated_study_time': '2-4 hours',
                    'practice_exercises': [],
                    'tokens_used': 0
                }
            end_time = time.time()
            
            learning_result['learning_time'] = round(end_time - start_time, 2)
            
            return jsonify({
                'success': True,
                **learning_result
            })
            
        except Exception as e:
            logger.error(f"Error in concept learning: {str(e)}")
            return jsonify({'error': 'Concept learning failed'}), 500
    
    @app.route('/api/system-status')
    def get_system_status():
        """Get comprehensive AI system status"""
        try:
            status = integrated_ai.get_system_status()
            return jsonify({
                'success': True,
                'status': status
            })
        except Exception as e:
            logger.error(f"Error getting system status: {str(e)}")
            return jsonify({'error': 'Failed to get system status'}), 500
    
    @app.route('/api/framework-suggestions', methods=['POST'])
    def get_framework_suggestions():
        """Get framework-specific suggestions and patterns"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No JSON data provided'}), 400
            
            framework = data.get('framework', '').strip()
            context = data.get('context', '').strip()
            
            if not framework:
                return jsonify({'error': 'Framework is required'}), 400
            
            # Sanitize inputs
            framework = sanitize_input(framework)
            context = sanitize_input(context) if context else ""
            
            # Get framework suggestions
            suggestions = integrated_ai.web_expert.get_framework_suggestions(framework, context)
            performance_tips = integrated_ai.web_expert.get_performance_tips(framework)
            
            return jsonify({
                'success': True,
                'framework': framework,
                'suggestions': suggestions,
                'performance_tips': performance_tips
            })
            
        except Exception as e:
            logger.error(f"Error getting framework suggestions: {str(e)}")
            return jsonify({'error': 'Failed to get framework suggestions'}), 500
    
    @app.route('/api/troubleshoot', methods=['POST'])
    def auto_troubleshoot():
        """Automatic troubleshooting assistance"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No JSON data provided'}), 400
            
            error_message = data.get('error_message', '').strip()
            code_context = data.get('code_context', '').strip()
            language = data.get('language', '').strip()
            file_path = data.get('file_path', '').strip()
            
            if not error_message or not language:
                return jsonify({'error': 'Error message and language are required'}), 400
            
            # Sanitize inputs
            error_message = sanitize_input(error_message)
            code_context = sanitize_input(code_context) if code_context else ""
            language = sanitize_input(language)
            file_path = sanitize_input(file_path) if file_path else ""
            
            # Get troubleshooting diagnosis
            start_time = time.time()
            diagnosis = integrated_ai.troubleshooting_ai.auto_diagnose_error(
                error_message=error_message,
                code_context=code_context,
                language=language,
                file_path=file_path
            )
            end_time = time.time()
            
            diagnosis['troubleshooting_time'] = round(end_time - start_time, 2)
            
            return jsonify({
                'success': True,
                'diagnosis': diagnosis
            })
            
        except Exception as e:
            logger.error(f"Error in troubleshooting: {str(e)}")
            return jsonify({'error': 'Troubleshooting failed'}), 500
    
    @app.route('/api/apply-fix', methods=['POST'])
    def apply_automatic_fix():
        """Apply automatic fixes when confidence is high"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No JSON data provided'}), 400
            
            session_id = data.get('session_id', '').strip()
            diagnosis = data.get('diagnosis', {})
            file_path = data.get('file_path', '').strip()
            language = data.get('language', '').strip()
            
            if not session_id or not diagnosis or not language:
                return jsonify({'error': 'Session ID, diagnosis, and language are required'}), 400
            
            # Apply automatic fix
            fix_result = integrated_ai.troubleshooting_ai.apply_automatic_fix(
                diagnosis=diagnosis,
                file_path=file_path,
                language=language
            )
            
            return jsonify({
                'success': True,
                'fix_result': fix_result
            })
            
        except Exception as e:
            logger.error(f"Error applying automatic fix: {str(e)}")
            return jsonify({'error': 'Failed to apply automatic fix'}), 500
    
    @app.route('/api/learning-feedback', methods=['POST'])
    def submit_learning_feedback():
        """Submit feedback for AI learning improvement"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No JSON data provided'}), 400
            
            query = data.get('query', '').strip()
            response = data.get('response', '').strip()
            feedback = data.get('feedback', '').strip()
            language = data.get('language', '').strip()
            session_id = data.get('session_id', '').strip()
            
            if not query or not response or not feedback:
                return jsonify({'error': 'Query, response, and feedback are required'}), 400
            
            # Submit feedback for learning
            integrated_ai.enhanced_ai.learn_from_interaction(
                query=query,
                response=response,
                feedback=feedback,
                language=language or 'general'
            )
            
            # Also update troubleshooting success if applicable
            if session_id:
                was_successful = 'good' in feedback.lower() or 'helpful' in feedback.lower()
                integrated_ai.troubleshooting_ai.learn_from_success(
                    session_id=session_id,
                    was_successful=was_successful,
                    user_feedback=feedback
                )
            
            return jsonify({
                'success': True,
                'message': 'Feedback submitted successfully'
            })
            
        except Exception as e:
            logger.error(f"Error submitting feedback: {str(e)}")
            return jsonify({'error': 'Failed to submit feedback'}), 500
    
    @app.route('/enhanced-interface')
    def enhanced_interface():
        """Enhanced multi-language programming interface"""
        return render_template('enhanced_interface.html')
    
    @app.route('/api/insights')
    def get_ai_insights():
        """Get comprehensive AI system insights"""
        try:
            insights = {}
            
            # Get insights from all AI components
            if integrated_ai.components['openai_enhanced']:
                insights['openai'] = integrated_ai.openai_ai.get_ai_insights()
            
            insights['troubleshooting'] = integrated_ai.troubleshooting_ai.get_troubleshooting_insights()
            insights['ml_training'] = integrated_ai.ml_system.get_model_insights()
            
            return jsonify({
                'success': True,
                'insights': insights,
                'components': integrated_ai.components
            })
            
        except Exception as e:
            logger.error(f"Error getting AI insights: {str(e)}")
            return jsonify({'error': 'Failed to get AI insights'}), 500
    
    @app.route('/api/multi-model-analytics')
    def get_multi_model_analytics():
        """Get multi-model AI analytics and performance data"""
        try:
            if not integrated_ai.components['multi_model_ai']:
                return jsonify({'error': 'Multi-model AI not available'}), 404
            
            analytics = integrated_ai.multi_model_ai.get_model_analytics()
            
            return jsonify({
                'success': True,
                'analytics': analytics
            })
            
        except Exception as e:
            logger.error(f"Error getting multi-model analytics: {str(e)}")
            return jsonify({'error': 'Failed to get analytics'}), 500
    
    @app.route('/api/model-suggestion', methods=['POST'])
    def get_model_suggestion():
        """Get optimal model suggestion for a specific task"""
        try:
            if not integrated_ai.components['multi_model_ai']:
                return jsonify({'error': 'Multi-model AI not available'}), 404
            
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No JSON data provided'}), 400
            
            task_type = data.get('task_type', 'general').strip()
            language = data.get('language', 'general').strip()
            
            suggestion = integrated_ai.multi_model_ai.suggest_optimal_model(task_type, language)
            
            return jsonify({
                'success': True,
                'suggestion': suggestion
            })
            
        except Exception as e:
            logger.error(f"Error getting model suggestion: {str(e)}")
            return jsonify({'error': 'Failed to get model suggestion'}), 500