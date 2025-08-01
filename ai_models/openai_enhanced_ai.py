"""
OpenAI-Enhanced AI System
Advanced AI capabilities using GPT-4o for comprehensive programming assistance
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import sqlite3

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
from openai import OpenAI

logger = logging.getLogger(__name__)

class OpenAIEnhancedAI:
    """
    Advanced AI system powered by OpenAI GPT-4o for comprehensive programming assistance
    """
    
    def __init__(self, db_path: str = "instance/openai_enhanced.db"):
        self.db_path = db_path
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OPENAI_API_KEY not found. Using fallback responses.")
            self.openai_client = None
        else:
            self.openai_client = OpenAI(api_key=api_key)
        
        self.initialize_openai_database()
        self.load_system_prompts()
    
    def initialize_openai_database(self):
        """Initialize OpenAI enhancement database"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # AI conversations and learning
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ai_conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    user_query TEXT NOT NULL,
                    ai_response TEXT NOT NULL,
                    language TEXT,
                    context TEXT,
                    tokens_used INTEGER DEFAULT 0,
                    response_time REAL,
                    quality_score REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Code generation tracking
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS code_generations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    request_type TEXT NOT NULL,
                    language TEXT NOT NULL,
                    generated_code TEXT NOT NULL,
                    explanation TEXT,
                    complexity_level TEXT DEFAULT 'intermediate',
                    testing_status TEXT DEFAULT 'pending',
                    user_satisfaction INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Learning improvements
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS learning_improvements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    improvement_type TEXT NOT NULL,
                    source_query TEXT NOT NULL,
                    improvement_data TEXT NOT NULL,
                    effectiveness_score REAL DEFAULT 0.0,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    def load_system_prompts(self):
        """Load system prompts for different programming tasks"""
        self.system_prompts = {
            'code_generation': """You are an expert full-stack developer with deep knowledge of:
- Python (Flask, Django, FastAPI, data science, ML/AI)
- JavaScript/TypeScript (React, Vue, Angular, Node.js)
- HTML5, CSS3, modern web frameworks
- Database design and optimization
- DevOps and deployment strategies
- Security best practices

Provide comprehensive, production-ready code with:
- Clear explanations and comments
- Error handling and edge cases
- Performance optimizations
- Security considerations
- Testing strategies
- Best practices and patterns""",
            
            'debugging': """You are an expert debugging specialist. When analyzing code issues:
- Identify root causes, not just symptoms
- Provide step-by-step debugging strategies
- Suggest preventive measures
- Explain the underlying concepts
- Offer multiple solution approaches
- Include testing recommendations""",
            
            'learning': """You are a patient, comprehensive programming instructor. When teaching:
- Start with fundamentals and build complexity gradually
- Provide practical, real-world examples
- Include interactive exercises and projects
- Explain the 'why' behind concepts
- Offer multiple learning paths based on experience level
- Connect concepts across different languages and frameworks""",
            
            'architecture': """You are a senior software architect. When designing systems:
- Consider scalability, maintainability, and performance
- Apply SOLID principles and design patterns
- Suggest appropriate technologies and frameworks
- Plan for security, testing, and deployment
- Provide clear documentation and diagrams
- Consider team skills and project constraints"""
        }
    
    def generate_enhanced_response(self, query: str, language: str = "general", 
                                 context: str = "", request_type: str = "general") -> Dict:
        """
        Generate enhanced response using OpenAI GPT-4o
        """
        start_time = datetime.now()
        conversation_id = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if not self.openai_client:
            return self._fallback_response(query, language, context, request_type)
        
        try:
            # Select appropriate system prompt
            system_prompt = self.system_prompts.get(request_type, self.system_prompts['code_generation'])
            
            # Build enhanced context
            enhanced_context = self._build_enhanced_context(query, language, context, request_type)
            
            # Generate response with GPT-4o
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o"
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": enhanced_context}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            ai_response = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            response_time = (datetime.now() - start_time).total_seconds()
            
            # Store conversation
            self._store_conversation(
                conversation_id, query, ai_response, language, context,
                tokens_used, response_time
            )
            
            # Enhance response with additional features
            enhanced_response = self._enhance_response(ai_response, language, request_type)
            
            return {
                'conversation_id': conversation_id,
                'response': enhanced_response,
                'language': language,
                'tokens_used': tokens_used,
                'response_time': response_time,
                'enhancements': self._get_response_enhancements(ai_response, language)
            }
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return self._fallback_response(query, language, context, request_type)
    
    def _build_enhanced_context(self, query: str, language: str, context: str, request_type: str) -> str:
        """Build enhanced context for better AI responses"""
        enhanced_query = f"""
Query: {query}

Programming Language/Framework: {language}

Request Type: {request_type}

Additional Context: {context}

Please provide a comprehensive response that includes:
1. Direct answer to the query
2. Code examples with explanations
3. Best practices and patterns
4. Common pitfalls to avoid
5. Testing recommendations
6. Performance considerations
7. Related concepts and next steps

Format your response with clear sections and code blocks using appropriate syntax highlighting.
        """
        
        return enhanced_query.strip()
    
    def _enhance_response(self, base_response: str, language: str, request_type: str) -> str:
        """Enhance the base response with additional features"""
        enhanced = base_response
        
        # Add language-specific tips
        language_tips = self._get_language_specific_tips(language)
        if language_tips:
            enhanced += f"\n\n## {language.title()} Specific Tips:\n" + "\n".join(language_tips)
        
        # Add troubleshooting section for code generation
        if request_type == 'code_generation':
            enhanced += "\n\n## Troubleshooting:\n"
            enhanced += "- Test the code incrementally\n"
            enhanced += "- Check for proper error handling\n"
            enhanced += "- Validate input parameters\n"
            enhanced += "- Monitor performance for large datasets\n"
        
        # Add learning resources
        resources = self._get_learning_resources(language, request_type)
        if resources:
            enhanced += f"\n\n## Additional Resources:\n" + "\n".join(resources)
        
        return enhanced
    
    def _get_language_specific_tips(self, language: str) -> List[str]:
        """Get language-specific tips and best practices"""
        tips = {
            'python': [
                "• Use virtual environments for dependency management",
                "• Follow PEP 8 style guidelines",
                "• Use type hints for better code documentation",
                "• Leverage list comprehensions for cleaner code"
            ],
            'javascript': [
                "• Use const/let instead of var",
                "• Implement proper error handling with try-catch",
                "• Use async/await for better readability",
                "• Apply ESLint for code quality"
            ],
            'react': [
                "• Use functional components with hooks",
                "• Implement proper key props for lists",
                "• Optimize with React.memo and useMemo",
                "• Follow component composition patterns"
            ],
            'css': [
                "• Use CSS Grid and Flexbox for layouts",
                "• Implement mobile-first responsive design",
                "• Use CSS custom properties (variables)",
                "• Optimize for accessibility"
            ]
        }
        
        return tips.get(language.lower(), [])
    
    def _get_learning_resources(self, language: str, request_type: str) -> List[str]:
        """Get relevant learning resources"""
        resources = {
            'python': [
                "• Official Python Documentation: https://docs.python.org/",
                "• Real Python Tutorials: https://realpython.com/",
                "• Python Package Index: https://pypi.org/"
            ],
            'javascript': [
                "• MDN Web Docs: https://developer.mozilla.org/",
                "• JavaScript.info: https://javascript.info/",
                "• Node.js Documentation: https://nodejs.org/docs/"
            ],
            'react': [
                "• Official React Documentation: https://react.dev/",
                "• React Patterns: https://reactpatterns.com/",
                "• React Testing Library: https://testing-library.com/"
            ]
        }
        
        return resources.get(language.lower(), [])
    
    def _get_response_enhancements(self, response: str, language: str) -> Dict:
        """Analyze response and provide enhancement suggestions"""
        enhancements = {
            'code_blocks_count': len([line for line in response.split('\n') if '```' in line]) // 2,
            'has_examples': 'example' in response.lower(),
            'has_best_practices': 'best practice' in response.lower(),
            'has_error_handling': 'error' in response.lower() or 'exception' in response.lower(),
            'estimated_complexity': self._estimate_complexity(response),
            'suggested_follow_ups': self._generate_follow_up_questions(response, language)
        }
        
        return enhancements
    
    def _estimate_complexity(self, response: str) -> str:
        """Estimate complexity level of the response"""
        code_indicators = ['class ', 'function', 'import ', 'async ', 'await ']
        advanced_patterns = ['decorator', 'metaclass', 'generator', 'context manager']
        
        code_count = sum(1 for indicator in code_indicators if indicator in response.lower())
        advanced_count = sum(1 for pattern in advanced_patterns if pattern in response.lower())
        
        if advanced_count > 2:
            return 'advanced'
        elif code_count > 3:
            return 'intermediate'
        else:
            return 'beginner'
    
    def _generate_follow_up_questions(self, response: str, language: str) -> List[str]:
        """Generate relevant follow-up questions"""
        follow_ups = [
            f"How can I test this {language} code effectively?",
            f"What are the performance implications of this approach?",
            f"How can I make this code more maintainable?",
            "What are some common pitfalls to avoid?",
            "Can you show me an advanced variation of this pattern?"
        ]
        
        return follow_ups[:3]  # Return top 3 follow-ups
    
    def generate_code_with_tests(self, description: str, language: str, 
                                complexity: str = "intermediate") -> Dict:
        """
        Generate code with comprehensive testing
        """
        if not self.openai_client:
            return self._fallback_code_generation(description, language)
        
        try:
            prompt = f"""
Generate {complexity}-level {language} code for: {description}

Please provide:
1. Complete, production-ready code with proper structure
2. Comprehensive unit tests
3. Integration tests if applicable
4. Error handling and edge cases
5. Documentation and comments
6. Performance considerations
7. Security best practices

Format the response with clear sections and proper code formatting.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": self.system_prompts['code_generation']},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=3000
            )
            
            generated_content = response.choices[0].message.content
            
            # Store generation
            self._store_code_generation(description, language, generated_content, complexity)
            
            return {
                'code': generated_content,
                'language': language,
                'complexity': complexity,
                'tokens_used': response.usage.total_tokens,
                'includes_tests': 'test' in generated_content.lower(),
                'includes_docs': 'documentation' in generated_content.lower() or '"""' in generated_content
            }
            
        except Exception as e:
            logger.error(f"Code generation error: {str(e)}")
            return self._fallback_code_generation(description, language)
    
    def debug_code_intelligently(self, code: str, error_message: str, 
                                language: str, context: str = "") -> Dict:
        """
        Intelligent code debugging with AI assistance
        """
        if not self.openai_client:
            return self._fallback_debugging(code, error_message, language)
        
        try:
            debug_prompt = f"""
Debug this {language} code that's producing an error:

ERROR MESSAGE:
{error_message}

CODE:
```{language}
{code}
```

CONTEXT:
{context}

Please provide:
1. Root cause analysis
2. Step-by-step debugging approach
3. Fixed code with explanations
4. Prevention strategies
5. Testing recommendations
6. Alternative approaches

Be thorough and educational in your response.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": self.system_prompts['debugging']},
                    {"role": "user", "content": debug_prompt}
                ],
                temperature=0.3,  # Lower temperature for debugging
                max_tokens=2500
            )
            
            debug_response = response.choices[0].message.content
            
            return {
                'debug_analysis': debug_response,
                'language': language,
                'error_type': self._classify_error_type(error_message),
                'estimated_fix_time': self._estimate_debug_time(error_message),
                'confidence': self._calculate_debug_confidence(debug_response),
                'tokens_used': response.usage.total_tokens
            }
            
        except Exception as e:
            logger.error(f"Debug assistance error: {str(e)}")
            return self._fallback_debugging(code, error_message, language)
    
    def _classify_error_type(self, error_message: str) -> str:
        """Classify the type of error"""
        error_types = {
            'syntax': ['syntax', 'invalid syntax', 'unexpected token'],
            'runtime': ['runtime', 'execution', 'null pointer', 'segmentation'],
            'logic': ['wrong output', 'incorrect result', 'unexpected behavior'],
            'import': ['import', 'module', 'package not found'],
            'type': ['type error', 'cannot convert', 'incompatible types']
        }
        
        error_lower = error_message.lower()
        for error_type, keywords in error_types.items():
            if any(keyword in error_lower for keyword in keywords):
                return error_type
        
        return 'unknown'
    
    def _estimate_debug_time(self, error_message: str) -> str:
        """Estimate time needed to debug the error"""
        error_type = self._classify_error_type(error_message)
        
        time_estimates = {
            'syntax': '5-15 minutes',
            'import': '2-10 minutes',
            'type': '10-30 minutes',
            'runtime': '15-45 minutes',
            'logic': '30-120 minutes',
            'unknown': '20-60 minutes'
        }
        
        return time_estimates.get(error_type, '20-60 minutes')
    
    def _calculate_debug_confidence(self, debug_response: str) -> float:
        """Calculate confidence in the debugging solution"""
        confidence_indicators = [
            'root cause', 'solution', 'fixed code', 'explanation',
            'step-by-step', 'test', 'prevent', 'alternative'
        ]
        
        response_lower = debug_response.lower()
        matches = sum(1 for indicator in confidence_indicators if indicator in response_lower)
        
        return min(matches / len(confidence_indicators), 1.0)
    
    def learn_programming_concept(self, concept: str, language: str, 
                                 experience_level: str = "intermediate") -> Dict:
        """
        Comprehensive learning assistance for programming concepts
        """
        if not self.openai_client:
            return self._fallback_learning(concept, language, experience_level)
        
        try:
            learning_prompt = f"""
Teach the concept of "{concept}" in {language} for a {experience_level} programmer.

Provide a comprehensive learning experience with:
1. Clear concept explanation with analogies
2. Fundamental principles and theory
3. Practical examples with progressive complexity
4. Interactive exercises and challenges
5. Real-world applications and use cases
6. Common mistakes and how to avoid them
7. Advanced techniques and optimizations
8. Related concepts and learning path
9. Practice projects to reinforce learning

Make it engaging, practical, and thorough.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": self.system_prompts['learning']},
                    {"role": "user", "content": learning_prompt}
                ],
                temperature=0.7,
                max_tokens=3000
            )
            
            learning_content = response.choices[0].message.content
            
            return {
                'learning_content': learning_content,
                'concept': concept,
                'language': language,
                'experience_level': experience_level,
                'estimated_study_time': self._estimate_study_time(concept, experience_level),
                'practice_exercises': self._extract_exercises(learning_content),
                'tokens_used': response.usage.total_tokens
            }
            
        except Exception as e:
            logger.error(f"Learning assistance error: {str(e)}")
            return self._fallback_learning(concept, language, experience_level)
    
    def _estimate_study_time(self, concept: str, experience_level: str) -> str:
        """Estimate time needed to learn the concept"""
        base_times = {
            'beginner': {'basic': '2-4 hours', 'intermediate': '4-8 hours', 'advanced': '8-16 hours'},
            'intermediate': {'basic': '1-2 hours', 'intermediate': '2-4 hours', 'advanced': '4-8 hours'},
            'advanced': {'basic': '30-60 minutes', 'intermediate': '1-2 hours', 'advanced': '2-4 hours'}
        }
        
        # Classify concept complexity
        complex_concepts = ['machine learning', 'async programming', 'design patterns', 'algorithms']
        intermediate_concepts = ['classes', 'functions', 'data structures', 'apis']
        
        if any(complex_concept in concept.lower() for complex_concept in complex_concepts):
            complexity = 'advanced'
        elif any(inter_concept in concept.lower() for inter_concept in intermediate_concepts):
            complexity = 'intermediate'
        else:
            complexity = 'basic'
        
        return base_times.get(experience_level, base_times['intermediate']).get(complexity, '2-4 hours')
    
    def _extract_exercises(self, learning_content: str) -> List[str]:
        """Extract practice exercises from learning content"""
        exercises = []
        lines = learning_content.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['exercise', 'practice', 'challenge', 'project']):
                if line.strip() and not line.startswith('#'):
                    exercises.append(line.strip())
        
        return exercises[:5]  # Return top 5 exercises
    
    def _fallback_response(self, query: str, language: str, context: str, request_type: str) -> Dict:
        """Fallback response when OpenAI is not available"""
        return {
            'conversation_id': f"fallback_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'response': f"I'm currently operating in fallback mode. For the {language} question about '{query}', I recommend checking the official documentation and community resources.",
            'language': language,
            'tokens_used': 0,
            'response_time': 0.1,
            'enhancements': {'fallback_mode': True}
        }
    
    def _fallback_code_generation(self, description: str, language: str) -> Dict:
        """Fallback code generation"""
        return {
            'code': f"# {language} code for: {description}\n# OpenAI unavailable - please implement manually",
            'language': language,
            'complexity': 'basic',
            'tokens_used': 0,
            'includes_tests': False,
            'includes_docs': True
        }
    
    def _fallback_debugging(self, code: str, error_message: str, language: str) -> Dict:
        """Fallback debugging assistance"""
        return {
            'debug_analysis': f"Error analysis for {language}: {error_message}\nPlease check syntax and logic manually.",
            'language': language,
            'error_type': 'unknown',
            'estimated_fix_time': '15-30 minutes',
            'confidence': 0.3,
            'tokens_used': 0
        }
    
    def _fallback_learning(self, concept: str, language: str, experience_level: str) -> Dict:
        """Fallback learning assistance"""
        return {
            'learning_content': f"Learning {concept} in {language} for {experience_level} level. Please consult official documentation.",
            'concept': concept,
            'language': language,
            'experience_level': experience_level,
            'estimated_study_time': '2-4 hours',
            'practice_exercises': [],
            'tokens_used': 0
        }
    
    def _store_conversation(self, conversation_id: str, query: str, response: str, 
                          language: str, context: str, tokens_used: int, response_time: float):
        """Store conversation for learning and improvement"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO ai_conversations 
                (conversation_id, user_query, ai_response, language, context, tokens_used, response_time)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (conversation_id, query, response, language, context, tokens_used, response_time))
            conn.commit()
    
    def _store_code_generation(self, description: str, language: str, code: str, complexity: str):
        """Store code generation for tracking and improvement"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO code_generations 
                (request_type, language, generated_code, complexity_level)
                VALUES (?, ?, ?, ?)
            ''', ('generation', language, code, complexity))
            conn.commit()
    
    def get_ai_insights(self) -> Dict:
        """Get insights about AI system performance"""
        insights = {
            'total_conversations': 0,
            'average_response_time': 0.0,
            'total_tokens_used': 0,
            'popular_languages': [],
            'recent_activity': []
        }
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total conversations
            cursor.execute('SELECT COUNT(*) FROM ai_conversations')
            insights['total_conversations'] = cursor.fetchone()[0]
            
            # Average response time
            cursor.execute('SELECT AVG(response_time) FROM ai_conversations')
            result = cursor.fetchone()
            if result and result[0]:
                insights['average_response_time'] = result[0]
            
            # Total tokens
            cursor.execute('SELECT SUM(tokens_used) FROM ai_conversations')
            result = cursor.fetchone()
            if result and result[0]:
                insights['total_tokens_used'] = result[0]
            
            # Popular languages
            cursor.execute('''
                SELECT language, COUNT(*) as count
                FROM ai_conversations
                WHERE language IS NOT NULL
                GROUP BY language
                ORDER BY count DESC
                LIMIT 5
            ''')
            insights['popular_languages'] = [
                {'language': row[0], 'count': row[1]} 
                for row in cursor.fetchall()
            ]
        
        return insights

# Initialize OpenAI enhanced AI system
openai_ai = OpenAIEnhancedAI()