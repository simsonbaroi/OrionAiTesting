"""
Enhanced Multi-Language AI Expert
Supports Python, JavaScript, React, HTML, CSS, and all modern frameworks
with self-learning and troubleshooting capabilities
"""

import os
import json
import logging
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedMultiLanguageAI:
    """
    Advanced AI system with comprehensive programming language support,
    self-learning capabilities, and automated troubleshooting
    """
    
    def __init__(self, db_path: str = "instance/enhanced_ai.db"):
        self.db_path = db_path
        self.initialize_database()
        
        # Language-specific knowledge bases
        self.knowledge_bases = {
            'python': {
                'frameworks': ['flask', 'django', 'fastapi', 'pytorch', 'tensorflow', 'scikit-learn'],
                'patterns': self._load_python_patterns(),
                'troubleshooting': self._load_python_troubleshooting()
            },
            'javascript': {
                'frameworks': ['react', 'vue', 'angular', 'node.js', 'express', 'next.js', 'svelte'],
                'patterns': self._load_javascript_patterns(),
                'troubleshooting': self._load_javascript_troubleshooting()
            },
            'web': {
                'technologies': ['html5', 'css3', 'sass', 'tailwind', 'bootstrap', 'webpack', 'vite'],
                'patterns': self._load_web_patterns(),
                'troubleshooting': self._load_web_troubleshooting()
            }
        }
    
    def initialize_database(self):
        """Initialize enhanced AI database with comprehensive tracking"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Enhanced knowledge table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS enhanced_knowledge (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    language TEXT NOT NULL,
                    framework TEXT,
                    category TEXT NOT NULL,
                    problem_type TEXT,
                    content TEXT NOT NULL,
                    solution TEXT,
                    confidence_score REAL DEFAULT 0.0,
                    usage_count INTEGER DEFAULT 0,
                    success_rate REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Learning patterns table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS learning_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_type TEXT NOT NULL,
                    pattern_data TEXT NOT NULL,
                    effectiveness_score REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Self-troubleshooting logs
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS troubleshooting_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    error_type TEXT NOT NULL,
                    error_message TEXT NOT NULL,
                    solution_applied TEXT,
                    success BOOLEAN DEFAULT FALSE,
                    execution_time REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    def _load_python_patterns(self) -> Dict:
        """Load Python programming patterns and best practices"""
        return {
            'data_science': {
                'pandas_operations': [
                    "df.groupby('column').agg({'col2': 'mean', 'col3': 'sum'})",
                    "df.pivot_table(values='value', index='row', columns='col')",
                    "df.merge(other_df, on='key', how='left')"
                ],
                'machine_learning': [
                    "from sklearn.model_selection import train_test_split",
                    "model.fit(X_train, y_train); predictions = model.predict(X_test)",
                    "from sklearn.metrics import accuracy_score, classification_report"
                ]
            },
            'web_development': {
                'flask_patterns': [
                    "@app.route('/api/<path>', methods=['GET', 'POST'])",
                    "return jsonify({'status': 'success', 'data': data})",
                    "request.get_json(); session['user_id'] = user.id"
                ],
                'api_design': [
                    "def create_response(data, status=200): return {'data': data}, status",
                    "try: # API call except Exception as e: return error_response(str(e))"
                ]
            }
        }
    
    def _load_javascript_patterns(self) -> Dict:
        """Load JavaScript/React patterns and best practices"""
        return {
            'react': {
                'hooks': [
                    "const [state, setState] = useState(initialValue)",
                    "useEffect(() => { /* effect */ return cleanup }, [dependencies])",
                    "const memoizedValue = useMemo(() => computeValue(a, b), [a, b])"
                ],
                'components': [
                    "const Component = ({ prop1, prop2, ...props }) => { return <div>{prop1}</div> }",
                    "export default React.memo(Component)",
                    "const handleClick = useCallback(() => { /* handler */ }, [deps])"
                ]
            },
            'modern_js': {
                'async_patterns': [
                    "const data = await fetch('/api/data').then(r => r.json())",
                    "try { const result = await asyncOperation() } catch (error) { handleError(error) }",
                    "Promise.all([promise1, promise2]).then(results => processResults(results))"
                ],
                'functional': [
                    "const processData = data => data.filter(item => item.active).map(transform)",
                    "const debounce = (fn, delay) => { let timer; return (...args) => { clearTimeout(timer); timer = setTimeout(() => fn(...args), delay) } }"
                ]
            }
        }
    
    def _load_web_patterns(self) -> Dict:
        """Load HTML/CSS patterns and best practices"""
        return {
            'responsive_design': {
                'css_grid': [
                    "display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr))",
                    "grid-gap: 1rem; align-items: center; justify-content: center"
                ],
                'flexbox': [
                    "display: flex; justify-content: space-between; align-items: center",
                    "flex-direction: column; flex-wrap: wrap; gap: 1rem"
                ]
            },
            'modern_css': {
                'custom_properties': [
                    ":root { --primary-color: #007bff; --spacing: 1rem }",
                    "color: var(--primary-color); margin: var(--spacing)"
                ],
                'animations': [
                    "@keyframes fadeIn { from { opacity: 0 } to { opacity: 1 } }",
                    "animation: fadeIn 0.3s ease-in-out"
                ]
            }
        }
    
    def _load_python_troubleshooting(self) -> Dict:
        """Load Python troubleshooting patterns"""
        return {
            'import_errors': {
                'ModuleNotFoundError': "Install missing package with pip install <package_name>",
                'ImportError': "Check module path and ensure proper package structure",
                'CircularImport': "Refactor imports or use lazy importing"
            },
            'runtime_errors': {
                'KeyError': "Check if key exists: key in dict or use dict.get(key, default)",
                'IndexError': "Validate list bounds: if 0 <= index < len(list)",
                'AttributeError': "Verify object has attribute: hasattr(obj, 'attr')"
            },
            'performance': {
                'slow_loops': "Use list comprehensions or vectorized operations with pandas/numpy",
                'memory_issues': "Use generators for large datasets: (item for item in data)",
                'database_slow': "Add database indexes and optimize queries"
            }
        }
    
    def _load_javascript_troubleshooting(self) -> Dict:
        """Load JavaScript troubleshooting patterns"""
        return {
            'common_errors': {
                'TypeError': "Check if variable is defined and of expected type",
                'ReferenceError': "Ensure variable is declared before use",
                'SyntaxError': "Check for missing brackets, semicolons, or quotes"
            },
            'react_issues': {
                'hook_errors': "Hooks must be called at top level, not inside loops/conditions",
                'state_updates': "Use functional updates for state: setState(prev => prev + 1)",
                'infinite_renders': "Add dependencies to useEffect to prevent infinite loops"
            },
            'async_issues': {
                'promise_errors': "Always handle Promise rejections with .catch() or try/catch",
                'fetch_errors': "Check response.ok before parsing JSON",
                'race_conditions': "Use proper async/await patterns and avoid shared state"
            }
        }
    
    def _load_web_troubleshooting(self) -> Dict:
        """Load HTML/CSS troubleshooting patterns"""
        return {
            'layout_issues': {
                'flexbox_problems': "Check flex container and item properties, ensure proper direction",
                'grid_issues': "Verify grid-template-columns/rows and grid-area definitions",
                'positioning': "Review position, z-index, and overflow properties"
            },
            'responsive_issues': {
                'mobile_layout': "Use mobile-first approach with min-width media queries",
                'image_scaling': "Use max-width: 100%; height: auto for responsive images",
                'text_overflow': "Apply text-overflow: ellipsis with overflow: hidden"
            }
        }
    
    def analyze_code(self, code: str, language: str, context: str = "") -> Dict:
        """
        Analyze code for patterns, potential issues, and improvements
        """
        analysis = {
            'language': language,
            'patterns_detected': [],
            'potential_issues': [],
            'suggestions': [],
            'confidence': 0.0
        }
        
        if language.lower() == 'python':
            analysis.update(self._analyze_python_code(code, context))
        elif language.lower() in ['javascript', 'js', 'react']:
            analysis.update(self._analyze_javascript_code(code, context))
        elif language.lower() in ['html', 'css']:
            analysis.update(self._analyze_web_code(code, context))
        
        # Store analysis for learning
        self._store_analysis(analysis)
        
        return analysis
    
    def _analyze_python_code(self, code: str, context: str) -> Dict:
        """Analyze Python code for patterns and issues"""
        analysis = {'patterns_detected': [], 'potential_issues': [], 'suggestions': []}
        
        # Check for common patterns
        if 'import pandas' in code or 'import numpy' in code:
            analysis['patterns_detected'].append('data_science')
        if 'from sklearn' in code or 'import torch' in code:
            analysis['patterns_detected'].append('machine_learning')
        if '@app.route' in code or 'from flask' in code:
            analysis['patterns_detected'].append('web_development')
        
        # Check for potential issues
        if re.search(r'except:', code):
            analysis['potential_issues'].append('Bare except clause - specify exception types')
        if re.search(r'\.append\(.*\).*for.*in', code):
            analysis['suggestions'].append('Consider using list comprehension for better performance')
        if 'eval(' in code:
            analysis['potential_issues'].append('eval() usage detected - security risk')
        
        return analysis
    
    def _analyze_javascript_code(self, code: str, context: str) -> Dict:
        """Analyze JavaScript/React code for patterns and issues"""
        analysis = {'patterns_detected': [], 'potential_issues': [], 'suggestions': []}
        
        # Check for React patterns
        if 'useState' in code or 'useEffect' in code:
            analysis['patterns_detected'].append('react_hooks')
        if 'fetch(' in code or 'axios' in code:
            analysis['patterns_detected'].append('api_calls')
        if 'addEventListener' in code:
            analysis['patterns_detected'].append('event_handling')
        
        # Check for potential issues
        if '==' in code and '===' not in code:
            analysis['suggestions'].append('Use strict equality (===) instead of loose equality (==)')
        if re.search(r'function.*\{.*var ', code):
            analysis['suggestions'].append('Consider using const/let instead of var')
        if 'innerHTML' in code:
            analysis['potential_issues'].append('innerHTML usage - potential XSS vulnerability')
        
        return analysis
    
    def _analyze_web_code(self, code: str, context: str) -> Dict:
        """Analyze HTML/CSS code for patterns and issues"""
        analysis = {'patterns_detected': [], 'potential_issues': [], 'suggestions': []}
        
        if 'display: grid' in code or 'grid-template' in code:
            analysis['patterns_detected'].append('css_grid')
        if 'display: flex' in code:
            analysis['patterns_detected'].append('flexbox')
        if '@media' in code:
            analysis['patterns_detected'].append('responsive_design')
        
        # Check for accessibility issues
        if '<img' in code and 'alt=' not in code:
            analysis['potential_issues'].append('Images missing alt attributes')
        if 'onclick=' in code:
            analysis['suggestions'].append('Consider using addEventListener instead of inline event handlers')
        
        return analysis
    
    def auto_troubleshoot(self, error_message: str, code_context: str, language: str) -> Dict:
        """
        Automatically troubleshoot errors and provide solutions
        """
        start_time = datetime.now()
        
        solution = {
            'error_type': self._classify_error(error_message, language),
            'solutions': [],
            'code_fixes': [],
            'prevention_tips': [],
            'confidence': 0.0
        }
        
        # Get relevant troubleshooting knowledge
        if language.lower() == 'python':
            troubleshooting_kb = self.knowledge_bases['python']['troubleshooting']
        elif language.lower() in ['javascript', 'react']:
            troubleshooting_kb = self.knowledge_bases['javascript']['troubleshooting']
        else:
            troubleshooting_kb = self.knowledge_bases['web']['troubleshooting']
        
        # Find matching solutions
        for category, error_solutions in troubleshooting_kb.items():
            for error_type, solution_text in error_solutions.items():
                if error_type.lower() in error_message.lower():
                    solution['solutions'].append(solution_text)
                    solution['confidence'] += 0.3
        
        # Generate code fixes based on context
        solution['code_fixes'] = self._generate_code_fixes(error_message, code_context, language)
        
        # Log troubleshooting attempt
        execution_time = (datetime.now() - start_time).total_seconds()
        self._log_troubleshooting(error_message, solution, execution_time)
        
        return solution
    
    def _classify_error(self, error_message: str, language: str) -> str:
        """Classify error type based on message and language"""
        error_message_lower = error_message.lower()
        
        if 'import' in error_message_lower or 'module' in error_message_lower:
            return 'import_error'
        elif 'syntax' in error_message_lower:
            return 'syntax_error'
        elif 'type' in error_message_lower:
            return 'type_error'
        elif 'reference' in error_message_lower:
            return 'reference_error'
        elif 'key' in error_message_lower:
            return 'key_error'
        elif 'index' in error_message_lower:
            return 'index_error'
        else:
            return 'runtime_error'
    
    def _generate_code_fixes(self, error_message: str, code_context: str, language: str) -> List[str]:
        """Generate specific code fixes based on error and context"""
        fixes = []
        
        if language.lower() == 'python':
            if 'ModuleNotFoundError' in error_message:
                module_name = re.search(r"No module named '([^']*)'", error_message)
                if module_name:
                    fixes.append(f"pip install {module_name.group(1)}")
            
            if 'KeyError' in error_message:
                fixes.append("Use dict.get(key, default_value) for safe key access")
                fixes.append("Check if key exists: if 'key' in dictionary:")
        
        elif language.lower() in ['javascript', 'react']:
            if 'ReferenceError' in error_message:
                fixes.append("Declare variable before use: let/const variableName")
                fixes.append("Check for typos in variable names")
            
            if 'TypeError' in error_message:
                fixes.append("Add type checking: if (typeof variable === 'expected_type')")
                fixes.append("Use optional chaining: object?.property")
        
        return fixes
    
    def learn_from_interaction(self, query: str, response: str, feedback: str, language: str):
        """
        Learn from user interactions to improve future responses
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Determine effectiveness score based on feedback
            effectiveness = 1.0 if 'good' in feedback.lower() or 'helpful' in feedback.lower() else 0.0
            if 'excellent' in feedback.lower() or 'perfect' in feedback.lower():
                effectiveness = 1.0
            elif 'bad' in feedback.lower() or 'wrong' in feedback.lower():
                effectiveness = 0.0
            else:
                effectiveness = 0.5
            
            # Store learning data
            cursor.execute('''
                INSERT INTO enhanced_knowledge 
                (language, category, content, solution, confidence_score, usage_count)
                VALUES (?, ?, ?, ?, ?, 1)
            ''', (language, 'user_interaction', query, response, effectiveness))
            
            # Update learning patterns
            pattern_data = json.dumps({
                'query_type': self._classify_query_type(query),
                'language': language,
                'response_length': len(response),
                'effectiveness': effectiveness
            })
            
            cursor.execute('''
                INSERT INTO learning_patterns (pattern_type, pattern_data, effectiveness_score)
                VALUES (?, ?, ?)
            ''', ('user_interaction', pattern_data, effectiveness))
            
            conn.commit()
    
    def _classify_query_type(self, query: str) -> str:
        """Classify the type of user query"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['error', 'bug', 'fix', 'problem']):
            return 'troubleshooting'
        elif any(word in query_lower for word in ['how to', 'tutorial', 'learn', 'guide']):
            return 'learning'
        elif any(word in query_lower for word in ['optimize', 'improve', 'performance']):
            return 'optimization'
        elif any(word in query_lower for word in ['create', 'build', 'generate', 'make']):
            return 'creation'
        else:
            return 'general'
    
    def _store_analysis(self, analysis: Dict):
        """Store code analysis results for learning"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO learning_patterns (pattern_type, pattern_data, effectiveness_score)
                VALUES (?, ?, ?)
            ''', ('code_analysis', json.dumps(analysis), analysis.get('confidence', 0.0)))
            
            conn.commit()
    
    def _log_troubleshooting(self, error_message: str, solution: Dict, execution_time: float):
        """Log troubleshooting attempts for learning"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO troubleshooting_logs 
                (error_type, error_message, solution_applied, success, execution_time)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                solution['error_type'], 
                error_message, 
                json.dumps(solution), 
                solution['confidence'] > 0.5,
                execution_time
            ))
            
            conn.commit()
    
    def get_smart_suggestions(self, partial_code: str, language: str, context: str = "") -> List[str]:
        """
        Provide intelligent code suggestions based on patterns and context
        """
        suggestions = []
        
        # Get relevant patterns from knowledge base
        if language.lower() == 'python':
            patterns = self.knowledge_bases['python']['patterns']
        elif language.lower() in ['javascript', 'react']:
            patterns = self.knowledge_bases['javascript']['patterns']
        else:
            patterns = self.knowledge_bases['web']['patterns']
        
        # Analyze partial code to determine intent
        code_intent = self._analyze_code_intent(partial_code, language)
        
        # Generate suggestions based on intent and patterns
        for category, pattern_group in patterns.items():
            if code_intent in category or category in context.lower():
                if isinstance(pattern_group, dict):
                    for subcategory, pattern_list in pattern_group.items():
                        suggestions.extend(pattern_list[:2])  # Add top 2 patterns
                else:
                    suggestions.extend(pattern_group[:3])  # Add top 3 patterns
        
        return suggestions[:10]  # Return top 10 suggestions
    
    def _analyze_code_intent(self, partial_code: str, language: str) -> str:
        """Analyze partial code to determine user intent"""
        code_lower = partial_code.lower()
        
        if 'import' in code_lower:
            return 'importing'
        elif 'def ' in code_lower or 'function' in code_lower:
            return 'function_definition'
        elif 'class ' in code_lower:
            return 'class_definition'
        elif 'for ' in code_lower or 'while ' in code_lower:
            return 'iteration'
        elif 'if ' in code_lower:
            return 'conditional'
        elif any(word in code_lower for word in ['fetch', 'axios', 'request']):
            return 'api_call'
        elif any(word in code_lower for word in ['useState', 'useEffect']):
            return 'react_hooks'
        else:
            return 'general'
    
    def generate_comprehensive_response(self, query: str, language: str = None, context: str = "") -> str:
        """
        Generate comprehensive response with multi-language support
        """
        # Auto-detect language if not specified
        if not language:
            language = self._detect_language(query) or "general"
        
        # Analyze query type
        query_type = self._classify_query_type(query)
        
        # Generate base response
        response = self._generate_base_response(query, language, query_type, context)
        
        # Add relevant code examples
        examples = self._get_relevant_examples(query, language, query_type)
        if examples:
            response += "\n\n**Code Examples:**\n" + "\n".join(examples)
        
        # Add troubleshooting tips if relevant
        if query_type == 'troubleshooting':
            troubleshooting_tips = self._get_troubleshooting_tips(query, language)
            if troubleshooting_tips:
                response += "\n\n**Troubleshooting Tips:**\n" + "\n".join(troubleshooting_tips)
        
        # Add learning resources
        resources = self._get_learning_resources(language, query_type)
        if resources:
            response += "\n\n**Additional Resources:**\n" + "\n".join(resources)
        
        return response
    
    def _detect_language(self, query: str) -> str:
        """Auto-detect programming language from query"""
        query_lower = query.lower()
        
        # Language-specific keywords
        if any(word in query_lower for word in ['react', 'jsx', 'usestate', 'useeffect']):
            return 'react'
        elif any(word in query_lower for word in ['javascript', 'js', 'node', 'npm']):
            return 'javascript'
        elif any(word in query_lower for word in ['python', 'django', 'flask', 'pandas']):
            return 'python'
        elif any(word in query_lower for word in ['html', 'css', 'styling', 'layout']):
            return 'web'
        else:
            return 'general'
    
    def _generate_base_response(self, query: str, language: str, query_type: str, context: str) -> str:
        """Generate base response based on query analysis"""
        # This would integrate with your existing AI models
        # For now, return a comprehensive template
        
        response_templates = {
            'troubleshooting': f"I'll help you troubleshoot this {language} issue. ",
            'learning': f"Here's a comprehensive guide for learning {language}. ",
            'optimization': f"I'll show you how to optimize your {language} code. ",
            'creation': f"Let me help you create this {language} solution. ",
            'general': f"Here's information about {language} programming. "
        }
        
        return response_templates.get(query_type, f"Here's help with your {language} question. ")
    
    def _get_relevant_examples(self, query: str, language: str, query_type: str) -> List[str]:
        """Get relevant code examples based on query"""
        examples = []
        
        if language == 'python':
            examples = [
                "```python\n# Example Python code\nprint('Hello, World!')\n```",
                "```python\n# Data processing example\nimport pandas as pd\ndf = pd.read_csv('data.csv')\n```"
            ]
        elif language in ['javascript', 'react']:
            examples = [
                "```javascript\n// Modern JavaScript example\nconst data = await fetch('/api').then(r => r.json());\n```",
                "```jsx\n// React component example\nconst Component = () => <div>Hello React!</div>;\n```"
            ]
        
        return examples[:3]  # Return top 3 examples
    
    def _get_troubleshooting_tips(self, query: str, language: str) -> List[str]:
        """Get relevant troubleshooting tips"""
        tips = []
        
        if language == 'python':
            tips = [
                "• Check Python version compatibility",
                "• Verify all imports are installed",
                "• Use print() statements for debugging"
            ]
        elif language in ['javascript', 'react']:
            tips = [
                "• Check browser console for errors",
                "• Verify all dependencies are installed",
                "• Use console.log() for debugging"
            ]
        
        return tips
    
    def _get_learning_resources(self, language: str, query_type: str) -> List[str]:
        """Get relevant learning resources"""
        resources = {
            'python': [
                "• Official Python Documentation: https://docs.python.org/",
                "• Python Tutorial: https://docs.python.org/3/tutorial/"
            ],
            'javascript': [
                "• MDN Web Docs: https://developer.mozilla.org/",
                "• JavaScript.info: https://javascript.info/"
            ],
            'react': [
                "• Official React Documentation: https://react.dev/",
                "• React Tutorial: https://react.dev/learn"
            ]
        }
        
        return resources.get(language, [])

# Initialize enhanced AI system
enhanced_ai = EnhancedMultiLanguageAI()