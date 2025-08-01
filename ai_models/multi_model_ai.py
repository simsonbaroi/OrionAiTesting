"""
Multi-Model AI System
Integrates OpenAI GPT-4o and DeepSeek models for enhanced programming assistance
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import sqlite3
import requests

# OpenAI integration
from openai import OpenAI

logger = logging.getLogger(__name__)

class MultiModelAI:
    """
    Advanced AI system that combines OpenAI GPT-4o and DeepSeek models
    for comprehensive programming assistance with intelligent model selection
    """
    
    def __init__(self, db_path: str = "instance/multi_model_ai.db"):
        self.db_path = db_path
        
        # Initialize API clients
        self.openai_client = None
        self.deepseek_available = False
        
        # OpenAI setup
        openai_key = os.environ.get("OPENAI_API_KEY")
        if openai_key:
            self.openai_client = OpenAI(api_key=openai_key)
            logger.info("OpenAI GPT-4o client initialized")
        
        # DeepSeek setup
        self.deepseek_api_key = os.environ.get("DEEPSEEK_API_KEY")
        if self.deepseek_api_key:
            self.deepseek_available = True
            logger.info("DeepSeek API key found and configured")
        
        self.initialize_database()
        self.load_model_preferences()
    
    def initialize_database(self):
        """Initialize multi-model AI database"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Model performance tracking
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS model_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_name TEXT NOT NULL,
                    task_type TEXT NOT NULL,
                    query_hash TEXT NOT NULL,
                    response_quality REAL DEFAULT 0.0,
                    response_time REAL NOT NULL,
                    tokens_used INTEGER DEFAULT 0,
                    user_satisfaction INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Model comparisons
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS model_comparisons (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL,
                    query_type TEXT NOT NULL,
                    openai_response TEXT,
                    deepseek_response TEXT,
                    openai_time REAL,
                    deepseek_time REAL,
                    openai_tokens INTEGER DEFAULT 0,
                    deepseek_tokens INTEGER DEFAULT 0,
                    preferred_model TEXT,
                    comparison_notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Model selection patterns
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS selection_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_category TEXT NOT NULL,
                    language TEXT NOT NULL,
                    complexity_level TEXT NOT NULL,
                    preferred_model TEXT NOT NULL,
                    success_rate REAL DEFAULT 0.0,
                    avg_response_time REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    def load_model_preferences(self):
        """Load model selection preferences based on task types"""
        self.model_preferences = {
            'code_generation': {
                'python': {'primary': 'openai', 'fallback': 'deepseek'},
                'javascript': {'primary': 'deepseek', 'fallback': 'openai'},
                'react': {'primary': 'openai', 'fallback': 'deepseek'},
                'general': {'primary': 'openai', 'fallback': 'deepseek'}
            },
            'debugging': {
                'python': {'primary': 'deepseek', 'fallback': 'openai'},
                'javascript': {'primary': 'openai', 'fallback': 'deepseek'},
                'general': {'primary': 'deepseek', 'fallback': 'openai'}
            },
            'learning': {
                'all': {'primary': 'openai', 'fallback': 'deepseek'}
            },
            'architecture': {
                'all': {'primary': 'openai', 'fallback': 'deepseek'}
            }
        }
    
    def select_optimal_model(self, task_type: str, language: str, complexity: str = 'intermediate') -> str:
        """
        Intelligently select the optimal model based on task characteristics
        """
        # Check historical performance
        best_model = self._get_best_performing_model(task_type, language)
        if best_model:
            return best_model
        
        # Use preferences as fallback
        task_prefs = self.model_preferences.get(task_type, {})
        lang_prefs = task_prefs.get(language, task_prefs.get('general', task_prefs.get('all', {})))
        
        primary_model = lang_prefs.get('primary', 'openai')
        
        # Check model availability
        if primary_model == 'openai' and self.openai_client:
            return 'openai'
        elif primary_model == 'deepseek' and self.deepseek_available:
            return 'deepseek'
        else:
            # Return available fallback
            fallback = lang_prefs.get('fallback', 'openai')
            if fallback == 'openai' and self.openai_client:
                return 'openai'
            elif fallback == 'deepseek' and self.deepseek_available:
                return 'deepseek'
            else:
                return 'openai' if self.openai_client else 'deepseek'
    
    def _get_best_performing_model(self, task_type: str, language: str) -> Optional[str]:
        """Get the best performing model for a specific task type and language"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT model_name, AVG(response_quality) as avg_quality, COUNT(*) as count
                    FROM model_performance 
                    WHERE task_type = ? AND query_hash LIKE ?
                    GROUP BY model_name
                    HAVING count >= 3
                    ORDER BY avg_quality DESC
                    LIMIT 1
                ''', (task_type, f'%{language}%'))
                
                result = cursor.fetchone()
                if result and result[1] > 0.7:  # Only return if quality is good
                    return result[0]
        except Exception as e:
            logger.error(f"Error getting best performing model: {str(e)}")
        
        return None
    
    async def generate_enhanced_response(self, query: str, language: str = "general", 
                                       context: str = "", task_type: str = "general",
                                       use_both_models: bool = False) -> Dict:
        """
        Generate enhanced response using optimal model selection or both models
        """
        start_time = datetime.now()
        
        if use_both_models and self.openai_client and self.deepseek_available:
            return await self._generate_with_both_models(query, language, context, task_type)
        else:
            selected_model = self.select_optimal_model(task_type, language)
            return await self._generate_with_single_model(
                query, language, context, task_type, selected_model
            )
    
    async def _generate_with_single_model(self, query: str, language: str, context: str, 
                                        task_type: str, model: str) -> Dict:
        """Generate response with a single selected model"""
        start_time = datetime.now()
        
        try:
            if model == 'openai' and self.openai_client:
                response = await self._call_openai(query, language, context, task_type)
            elif model == 'deepseek' and self.deepseek_available:
                response = await self._call_deepseek(query, language, context, task_type)
            else:
                return self._create_error_response("No available models for this request")
            
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()
            
            # Store performance metrics
            self._store_performance_metrics(
                model, task_type, query, response.get('quality', 0.8), 
                response_time, response.get('tokens_used', 0)
            )
            
            return {
                'success': True,
                'response': response.get('content', ''),
                'model_used': model,
                'response_time': response_time,
                'tokens_used': response.get('tokens_used', 0),
                'quality_score': response.get('quality', 0.8),
                'task_type': task_type,
                'language': language
            }
            
        except Exception as e:
            logger.error(f"Error generating response with {model}: {str(e)}")
            return self._create_error_response(f"Error with {model} model: {str(e)}")
    
    async def _generate_with_both_models(self, query: str, language: str, context: str, 
                                       task_type: str) -> Dict:
        """Generate responses with both models and provide comparison"""
        start_time = datetime.now()
        
        try:
            # Call both models concurrently
            openai_task = self._call_openai(query, language, context, task_type)
            deepseek_task = self._call_deepseek(query, language, context, task_type)
            
            openai_response, deepseek_response = await asyncio.gather(
                openai_task, deepseek_task, return_exceptions=True
            )
            
            end_time = datetime.now()
            total_time = (end_time - start_time).total_seconds()
            
            # Process responses
            result = {
                'success': True,
                'response_type': 'comparison',
                'total_time': total_time,
                'task_type': task_type,
                'language': language
            }
            
            # Handle OpenAI response
            if isinstance(openai_response, Exception):
                result['openai_error'] = str(openai_response)
            else:
                result['openai_response'] = openai_response.get('content', '')
                result['openai_tokens'] = openai_response.get('tokens_used', 0)
                result['openai_time'] = openai_response.get('response_time', 0)
            
            # Handle DeepSeek response
            if isinstance(deepseek_response, Exception):
                result['deepseek_error'] = str(deepseek_response)
            else:
                result['deepseek_response'] = deepseek_response.get('content', '')
                result['deepseek_tokens'] = deepseek_response.get('tokens_used', 0)
                result['deepseek_time'] = deepseek_response.get('response_time', 0)
            
            # Store comparison
            self._store_model_comparison(query, task_type, result)
            
            # Select best response for primary response
            if not isinstance(openai_response, Exception) and not isinstance(deepseek_response, Exception):
                # Use quality scores or default to OpenAI
                openai_quality = openai_response.get('quality', 0.8)
                deepseek_quality = deepseek_response.get('quality', 0.8)
                
                if deepseek_quality > openai_quality:
                    result['response'] = deepseek_response.get('content', '')
                    result['primary_model'] = 'deepseek'
                else:
                    result['response'] = openai_response.get('content', '')
                    result['primary_model'] = 'openai'
            elif not isinstance(openai_response, Exception):
                result['response'] = openai_response.get('content', '')
                result['primary_model'] = 'openai'
            elif not isinstance(deepseek_response, Exception):
                result['response'] = deepseek_response.get('content', '')
                result['primary_model'] = 'deepseek'
            else:
                result['success'] = False
                result['error'] = 'Both models failed to generate responses'
            
            return result
            
        except Exception as e:
            logger.error(f"Error in dual model generation: {str(e)}")
            return self._create_error_response(f"Dual model error: {str(e)}")
    
    async def _call_openai(self, query: str, language: str, context: str, task_type: str) -> Dict:
        """Call OpenAI GPT-4o API"""
        if not self.openai_client:
            raise Exception("OpenAI client not available")
        
        try:
            # Build enhanced prompt
            system_prompt = self._build_system_prompt(task_type, language)
            user_prompt = self._build_user_prompt(query, language, context, task_type)
            
            start_time = datetime.now()
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # Latest OpenAI model
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=2500
            )
            
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()
            
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
            return {
                'content': content,
                'tokens_used': tokens_used,
                'response_time': response_time,
                'quality': self._estimate_response_quality(content, task_type),
                'model': 'openai'
            }
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise e
    
    async def _call_deepseek(self, query: str, language: str, context: str, task_type: str) -> Dict:
        """Call DeepSeek API"""
        if not self.deepseek_available:
            raise Exception("DeepSeek API not available")
        
        try:
            # Build enhanced prompt
            system_prompt = self._build_system_prompt(task_type, language)
            user_prompt = self._build_user_prompt(query, language, context, task_type)
            
            start_time = datetime.now()
            
            headers = {
                'Authorization': f'Bearer {self.deepseek_api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': 'deepseek-coder',  # DeepSeek's coding model
                'messages': [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                'temperature': 0.7,
                'max_tokens': 2500
            }
            
            response = requests.post(
                'https://api.deepseek.com/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()
            
            if response.status_code == 200:
                data = response.json()
                content = data['choices'][0]['message']['content']
                tokens_used = data.get('usage', {}).get('total_tokens', 0)
                
                return {
                    'content': content,
                    'tokens_used': tokens_used,
                    'response_time': response_time,
                    'quality': self._estimate_response_quality(content, task_type),
                    'model': 'deepseek'
                }
            else:
                raise Exception(f"DeepSeek API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"DeepSeek API error: {str(e)}")
            raise e
    
    def _build_system_prompt(self, task_type: str, language: str) -> str:
        """Build system prompt based on task type and language"""
        base_prompt = "You are an expert programmer and AI assistant specializing in comprehensive software development."
        
        task_prompts = {
            'code_generation': f"Focus on generating clean, efficient, and well-documented {language} code with proper error handling and best practices.",
            'debugging': f"Analyze code issues systematically and provide step-by-step debugging solutions for {language} problems.",
            'learning': f"Explain {language} concepts clearly with practical examples and progressive complexity.",
            'architecture': f"Design scalable and maintainable software architectures using {language} and related technologies."
        }
        
        return f"{base_prompt} {task_prompts.get(task_type, 'Provide comprehensive programming assistance.')}"
    
    def _build_user_prompt(self, query: str, language: str, context: str, task_type: str) -> str:
        """Build comprehensive user prompt"""
        prompt = f"Query: {query}\n"
        prompt += f"Programming Language: {language}\n"
        prompt += f"Task Type: {task_type}\n"
        
        if context:
            prompt += f"Context: {context}\n"
        
        prompt += "\nPlease provide a comprehensive response including:"
        prompt += "\n1. Direct answer to the query"
        prompt += "\n2. Code examples with explanations"
        prompt += "\n3. Best practices and common pitfalls"
        prompt += "\n4. Testing recommendations"
        prompt += "\n5. Related concepts and next steps"
        
        return prompt
    
    def _estimate_response_quality(self, content: str, task_type: str) -> float:
        """Estimate response quality based on content analysis"""
        if not content:
            return 0.0
        
        quality_score = 0.5  # Base score
        
        # Check for code blocks
        if '```' in content:
            quality_score += 0.1
        
        # Check for explanations
        if any(word in content.lower() for word in ['because', 'since', 'this is', 'explanation']):
            quality_score += 0.1
        
        # Check for best practices
        if 'best practice' in content.lower() or 'recommended' in content.lower():
            quality_score += 0.1
        
        # Check for examples
        if 'example' in content.lower():
            quality_score += 0.1
        
        # Length consideration
        if len(content) > 500:
            quality_score += 0.1
        
        return min(quality_score, 1.0)
    
    def _store_performance_metrics(self, model: str, task_type: str, query: str, 
                                 quality: float, response_time: float, tokens_used: int):
        """Store model performance metrics"""
        try:
            query_hash = str(hash(query + task_type))
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO model_performance 
                    (model_name, task_type, query_hash, response_quality, response_time, tokens_used)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (model, task_type, query_hash, quality, response_time, tokens_used))
                conn.commit()
        except Exception as e:
            logger.error(f"Error storing performance metrics: {str(e)}")
    
    def _store_model_comparison(self, query: str, task_type: str, comparison_data: Dict):
        """Store model comparison data"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO model_comparisons 
                    (query, query_type, openai_response, deepseek_response, 
                     openai_time, deepseek_time, openai_tokens, deepseek_tokens, preferred_model)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    query, task_type,
                    comparison_data.get('openai_response', ''),
                    comparison_data.get('deepseek_response', ''),
                    comparison_data.get('openai_time', 0),
                    comparison_data.get('deepseek_time', 0),
                    comparison_data.get('openai_tokens', 0),
                    comparison_data.get('deepseek_tokens', 0),
                    comparison_data.get('primary_model', '')
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Error storing model comparison: {str(e)}")
    
    def _create_error_response(self, error_message: str) -> Dict:
        """Create standardized error response"""
        return {
            'success': False,
            'error': error_message,
            'response': f"I'm sorry, but I encountered an error: {error_message}",
            'model_used': 'none',
            'response_time': 0,
            'tokens_used': 0
        }
    
    def get_model_analytics(self) -> Dict:
        """Get comprehensive analytics about model performance"""
        analytics = {
            'models_available': {
                'openai': bool(self.openai_client),
                'deepseek': self.deepseek_available
            },
            'performance_metrics': {},
            'usage_statistics': {},
            'recommendations': []
        }
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Performance metrics by model
                cursor.execute('''
                    SELECT model_name, 
                           AVG(response_quality) as avg_quality,
                           AVG(response_time) as avg_time,
                           AVG(tokens_used) as avg_tokens,
                           COUNT(*) as total_requests
                    FROM model_performance 
                    GROUP BY model_name
                ''')
                
                for row in cursor.fetchall():
                    model_name = row[0]
                    analytics['performance_metrics'][model_name] = {
                        'avg_quality': round(row[1], 3),
                        'avg_response_time': round(row[2], 3),
                        'avg_tokens': int(row[3]),
                        'total_requests': row[4]
                    }
                
                # Task type preferences
                cursor.execute('''
                    SELECT task_type, model_name, AVG(response_quality) as quality
                    FROM model_performance 
                    GROUP BY task_type, model_name
                    ORDER BY task_type, quality DESC
                ''')
                
                task_preferences = {}
                for row in cursor.fetchall():
                    task_type = row[0]
                    if task_type not in task_preferences:
                        task_preferences[task_type] = []
                    task_preferences[task_type].append({
                        'model': row[1],
                        'quality': round(row[2], 3)
                    })
                
                analytics['task_preferences'] = task_preferences
        
        except Exception as e:
            logger.error(f"Error getting model analytics: {str(e)}")
        
        return analytics
    
    def suggest_optimal_model(self, task_type: str, language: str) -> Dict:
        """Suggest optimal model based on analytics"""
        analytics = self.get_model_analytics()
        
        suggestion = {
            'suggested_model': self.select_optimal_model(task_type, language),
            'reasoning': '',
            'confidence': 'medium'
        }
        
        # Add reasoning based on analytics
        task_prefs = analytics.get('task_preferences', {}).get(task_type, [])
        if task_prefs:
            best_model = task_prefs[0]['model']
            best_quality = task_prefs[0]['quality']
            
            suggestion['suggested_model'] = best_model
            suggestion['reasoning'] = f"Based on historical performance, {best_model} shows {best_quality:.1%} quality for {task_type} tasks"
            suggestion['confidence'] = 'high' if best_quality > 0.8 else 'medium'
        
        return suggestion

# Initialize multi-model AI system
multi_model_ai = MultiModelAI()