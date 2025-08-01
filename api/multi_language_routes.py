from flask import Blueprint, request, jsonify, render_template
import logging
from typing import Dict, List, Any
from models import (
    KnowledgeBase, TrainingData, UserQuery, ProjectTemplate, 
    CodeExample, LearningPath, UserProgress, SystemConfig
)
from app import db
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

# Create blueprint for multi-language learning routes
multi_lang_bp = Blueprint('multi_language', __name__, url_prefix='/api/v1')


@multi_lang_bp.route('/languages', methods=['GET'])
def get_supported_languages():
    """Get all supported programming languages"""
    try:
        languages = db.session.query(KnowledgeBase.language).distinct().all()
        language_stats = {}
        
        for (lang,) in languages:
            if lang:
                count = KnowledgeBase.query.filter_by(language=lang, is_active=True).count()
                language_stats[lang] = {
                    'knowledge_count': count,
                    'has_templates': ProjectTemplate.query.filter_by(language=lang).count() > 0,
                    'has_examples': CodeExample.query.filter_by(language=lang).count() > 0,
                    'learning_paths': LearningPath.query.filter_by(language=lang, is_active=True).count()
                }
        
        return jsonify({
            'success': True,
            'languages': language_stats,
            'total_languages': len(language_stats)
        })
        
    except Exception as e:
        logger.error(f"Error getting supported languages: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@multi_lang_bp.route('/knowledge/<language>', methods=['GET'])
def get_knowledge_by_language(language):
    """Get knowledge base items for a specific language"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        difficulty = request.args.get('difficulty')
        category = request.args.get('category')
        
        query = KnowledgeBase.query.filter_by(language=language.lower(), is_active=True)
        
        if difficulty:
            query = query.filter_by(difficulty=difficulty)
        if category:
            query = query.filter_by(category=category)
            
        knowledge_items = query.order_by(KnowledgeBase.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        items_data = []
        for item in knowledge_items.items:
            items_data.append({
                'id': item.id,
                'title': item.title,
                'content': item.content[:500] + '...' if len(item.content) > 500 else item.content,
                'difficulty': item.difficulty,
                'category': item.category,
                'tags': item.tags,
                'quality_score': item.quality_score,
                'source_type': item.source_type,
                'created_at': item.created_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'language': language,
            'items': items_data,
            'pagination': {
                'page': knowledge_items.page,
                'pages': knowledge_items.pages,
                'total': knowledge_items.total,
                'has_next': knowledge_items.has_next,
                'has_prev': knowledge_items.has_prev
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting knowledge for {language}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@multi_lang_bp.route('/templates', methods=['GET'])
def get_project_templates():
    """Get available project templates"""
    try:
        language = request.args.get('language')
        category = request.args.get('category')
        difficulty = request.args.get('difficulty')
        
        query = ProjectTemplate.query
        
        if language:
            query = query.filter_by(language=language.lower())
        if category:
            query = query.filter_by(category=category)
        if difficulty:
            query = query.filter_by(difficulty=difficulty)
            
        templates = query.order_by(ProjectTemplate.popularity_score.desc()).all()
        
        templates_data = []
        for template in templates:
            templates_data.append({
                'id': template.id,
                'name': template.name,
                'description': template.description,
                'language': template.language,
                'category': template.category,
                'difficulty': template.difficulty,
                'popularity_score': template.popularity_score,
                'usage_count': template.usage_count,
                'dependencies': template.dependencies,
                'is_featured': template.is_featured,
                'created_at': template.created_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'templates': templates_data,
            'total': len(templates_data)
        })
        
    except Exception as e:
        logger.error(f"Error getting project templates: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@multi_lang_bp.route('/templates/<int:template_id>/code', methods=['GET'])
def get_template_code(template_id):
    """Get full template code and instructions"""
    try:
        template = ProjectTemplate.query.get_or_404(template_id)
        
        # Increment usage count
        template.usage_count += 1
        db.session.commit()
        
        return jsonify({
            'success': True,
            'template': {
                'id': template.id,
                'name': template.name,
                'description': template.description,
                'language': template.language,
                'category': template.category,
                'template_code': template.template_code,
                'file_structure': template.file_structure,
                'dependencies': template.dependencies,
                'instructions': template.instructions,
                'difficulty': template.difficulty
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting template code: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@multi_lang_bp.route('/examples', methods=['GET'])
def get_code_examples():
    """Get code examples by language and category"""
    try:
        language = request.args.get('language')
        category = request.args.get('category')
        difficulty = request.args.get('difficulty')
        
        query = CodeExample.query
        
        if language:
            query = query.filter_by(language=language.lower())
        if category:
            query = query.filter_by(category=category)
        if difficulty:
            query = query.filter_by(difficulty=difficulty)
            
        examples = query.order_by(CodeExample.created_at.desc()).all()
        
        examples_data = []
        for example in examples:
            examples_data.append({
                'id': example.id,
                'title': example.title,
                'description': example.description,
                'language': example.language,
                'category': example.category,
                'code_snippet': example.code_snippet,
                'explanation': example.explanation,
                'input_example': example.input_example,
                'output_example': example.output_example,
                'related_concepts': example.related_concepts,
                'difficulty': example.difficulty,
                'is_tested': example.is_tested
            })
        
        return jsonify({
            'success': True,
            'examples': examples_data,
            'total': len(examples_data)
        })
        
    except Exception as e:
        logger.error(f"Error getting code examples: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@multi_lang_bp.route('/learning-paths', methods=['GET'])
def get_learning_paths():
    """Get structured learning paths"""
    try:
        language = request.args.get('language')
        target_audience = request.args.get('target_audience')
        
        query = LearningPath.query.filter_by(is_active=True)
        
        if language:
            query = query.filter_by(language=language.lower())
        if target_audience:
            query = query.filter_by(target_audience=target_audience)
            
        paths = query.order_by(LearningPath.created_at.desc()).all()
        
        paths_data = []
        for path in paths:
            paths_data.append({
                'id': path.id,
                'name': path.name,
                'description': path.description,
                'language': path.language,
                'target_audience': path.target_audience,
                'estimated_duration': path.estimated_duration,
                'curriculum': path.curriculum,
                'prerequisites': path.prerequisites,
                'learning_objectives': path.learning_objectives,
                'completion_criteria': path.completion_criteria
            })
        
        return jsonify({
            'success': True,
            'learning_paths': paths_data,
            'total': len(paths_data)
        })
        
    except Exception as e:
        logger.error(f"Error getting learning paths: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@multi_lang_bp.route('/chat/multi-language', methods=['POST'])
def multi_language_chat():
    """Enhanced chat that supports multiple programming languages"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        language = data.get('language', 'python').lower()
        context = data.get('context', {})
        
        if not question:
            return jsonify({'success': False, 'error': 'Question is required'}), 400
        
        # Search for relevant knowledge in the specified language
        relevant_knowledge = KnowledgeBase.query.filter(
            KnowledgeBase.language == language,
            KnowledgeBase.is_active == True,
            db.or_(
                KnowledgeBase.title.ilike(f'%{question}%'),
                KnowledgeBase.content.ilike(f'%{question}%')
            )
        ).order_by(KnowledgeBase.quality_score.desc()).limit(3).all()
        
        # Generate response based on found knowledge
        if relevant_knowledge:
            best_match = relevant_knowledge[0]
            response = generate_enhanced_response(best_match, question, language)
            answer_source = 'knowledge_base'
        else:
            response = generate_language_specific_fallback(question, language)
            answer_source = 'pattern_match'
        
        # Store the interaction
        user_query = UserQuery(
            question=question,
            answer=response,
            language=language,
            session_id=context.get('session_id'),
            answer_source=answer_source,
            context=context
        )
        db.session.add(user_query)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'answer': response,
            'language': language,
            'source': answer_source,
            'related_knowledge': len(relevant_knowledge),
            'query_id': user_query.id
        })
        
    except Exception as e:
        logger.error(f"Error in multi-language chat: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


def generate_enhanced_response(knowledge_item, question, language):
    """Generate enhanced response using knowledge base item"""
    return f"""**{knowledge_item.title}** ({language.upper()})

{knowledge_item.content}

**Difficulty:** {knowledge_item.difficulty.title()}
**Category:** {knowledge_item.category or 'General'}

This information comes from our {language} knowledge base. Would you like more specific examples or have follow-up questions?"""


def generate_language_specific_fallback(question, language):
    """Generate language-specific fallback responses"""
    
    fallback_responses = {
        'python': """I understand you're asking about Python. While I don't have specific knowledge base content for this question, I can help with:

• Python syntax and fundamentals
• Data structures (lists, dictionaries, sets)
• Object-oriented programming
• Web development with Flask/Django
• Data analysis with pandas/NumPy
• Automation scripts

Could you be more specific about what aspect of Python you'd like to learn?""",
        
        'javascript': """Great JavaScript question! I can help you with:

• ES6+ syntax and features
• DOM manipulation
• Async programming (Promises, async/await)
• Frontend frameworks (React, Vue)
• Node.js backend development
• Web APIs and AJAX

What specific JavaScript concept would you like to explore?""",
        
        'html': """I can help with HTML concepts including:

• Semantic HTML5 elements
• Form creation and validation
• Accessibility best practices
• HTML structure and organization
• Integration with CSS and JavaScript

What HTML topic interests you most?""",
        
        'css': """I can assist with CSS topics like:

• Flexbox and Grid layouts
• Responsive design principles
• CSS animations and transitions
• Preprocessing (Sass, Less)
• CSS frameworks (Bootstrap, Tailwind)

What CSS concept would you like to learn about?""",
        
        'react': """I can help with React development including:

• Component creation and props
• State management (useState, useEffect)
• Context API and Redux
• React Router for navigation
• Best practices and patterns

What React topic would you like to explore?"""
    }
    
    return fallback_responses.get(language, f"I can help you with {language} programming. Could you please be more specific about what you'd like to learn?")


@multi_lang_bp.route('/stats/multi-language', methods=['GET'])
def get_multi_language_stats():
    """Get statistics across all supported languages"""
    try:
        # Get stats for each language
        languages = db.session.query(KnowledgeBase.language).distinct().all()
        language_stats = {}
        
        for (lang,) in languages:
            if lang:
                language_stats[lang] = {
                    'knowledge_items': KnowledgeBase.query.filter_by(language=lang, is_active=True).count(),
                    'code_examples': CodeExample.query.filter_by(language=lang).count(),
                    'project_templates': ProjectTemplate.query.filter_by(language=lang).count(),
                    'learning_paths': LearningPath.query.filter_by(language=lang, is_active=True).count(),
                    'user_queries': UserQuery.query.filter_by(language=lang).count(),
                    'avg_quality_score': db.session.query(db.func.avg(KnowledgeBase.quality_score)).filter_by(language=lang).scalar() or 0
                }
        
        # Overall stats
        total_stats = {
            'total_knowledge_items': KnowledgeBase.query.filter_by(is_active=True).count(),
            'total_user_queries': UserQuery.query.count(),
            'total_code_examples': CodeExample.query.count(),
            'total_project_templates': ProjectTemplate.query.count(),
            'supported_languages': len(language_stats),
            'most_popular_language': max(language_stats.keys(), key=lambda k: language_stats[k]['user_queries']) if language_stats else None
        }
        
        return jsonify({
            'success': True,
            'language_stats': language_stats,
            'total_stats': total_stats,
            'generated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting multi-language stats: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500