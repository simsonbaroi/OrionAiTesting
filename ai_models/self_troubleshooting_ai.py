"""
Self-Troubleshooting AI System
Automatically detects, diagnoses, and fixes code issues across multiple languages
"""

import os
import json
import sqlite3
import subprocess
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class SelfTroubleshootingAI:
    """
    Advanced self-troubleshooting system that can automatically detect,
    diagnose, and fix code issues across multiple programming languages
    """
    
    def __init__(self, db_path: str = "instance/troubleshooting.db"):
        self.db_path = db_path
        self.initialize_troubleshooting_database()
        self.load_troubleshooting_patterns()
    
    def initialize_troubleshooting_database(self):
        """Initialize troubleshooting database"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Error patterns and solutions
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS error_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    language TEXT NOT NULL,
                    error_type TEXT NOT NULL,
                    error_pattern TEXT NOT NULL,
                    solution_steps TEXT NOT NULL,
                    code_fix TEXT,
                    success_rate REAL DEFAULT 0.0,
                    usage_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Troubleshooting sessions
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS troubleshooting_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    original_error TEXT NOT NULL,
                    language TEXT NOT NULL,
                    steps_taken TEXT NOT NULL,
                    final_solution TEXT,
                    success BOOLEAN DEFAULT FALSE,
                    duration_seconds REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Learning feedback
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS troubleshooting_feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    feedback_type TEXT NOT NULL,
                    feedback_content TEXT NOT NULL,
                    effectiveness_score REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    def load_troubleshooting_patterns(self):
        """Load comprehensive troubleshooting patterns"""
        self.troubleshooting_patterns = {
            'python': {
                'import_errors': {
                    'ModuleNotFoundError': {
                        'pattern': r"No module named '([^']*)'",
                        'solutions': [
                            "Install missing package: pip install {module}",
                            "Check if package name is correct",
                            "Verify virtual environment is activated",
                            "Check if package is in requirements.txt"
                        ],
                        'code_fix': "# Add to requirements.txt or install:\n# pip install {module}"
                    },
                    'ImportError': {
                        'pattern': r"cannot import name '([^']*)' from '([^']*)'",
                        'solutions': [
                            "Check if the imported function/class exists",
                            "Verify the module structure",
                            "Check for circular imports",
                            "Update import statement"
                        ]
                    }
                },
                'syntax_errors': {
                    'SyntaxError': {
                        'pattern': r"invalid syntax.*line (\d+)",
                        'solutions': [
                            "Check for missing parentheses, brackets, or quotes",
                            "Verify proper indentation",
                            "Check for missing colons after if/for/while/def",
                            "Ensure proper string quotation matching"
                        ]
                    },
                    'IndentationError': {
                        'pattern': r"unexpected indent|expected an indented block",
                        'solutions': [
                            "Use consistent indentation (4 spaces recommended)",
                            "Check for mixed tabs and spaces",
                            "Ensure proper code block structure",
                            "Add pass statement if block is empty"
                        ]
                    }
                },
                'runtime_errors': {
                    'TypeError': {
                        'pattern': r"'([^']*)' object (.*)",
                        'solutions': [
                            "Check data types being used",
                            "Add type checking before operations",
                            "Convert types if necessary",
                            "Use hasattr() to check for methods"
                        ]
                    },
                    'KeyError': {
                        'pattern': r"KeyError: '([^']*)'",
                        'solutions': [
                            "Use dict.get(key, default) for safe access",
                            "Check if key exists: 'key' in dict",
                            "Print dict.keys() to see available keys",
                            "Handle missing keys with try-except"
                        ],
                        'code_fix': '''
# Safe dictionary access
value = my_dict.get('{key}', default_value)

# Or check key existence
if '{key}' in my_dict:
    value = my_dict['{key}']
                        '''
                    }
                }
            },
            'javascript': {
                'syntax_errors': {
                    'SyntaxError': {
                        'pattern': r"Unexpected token|Unexpected end of input",
                        'solutions': [
                            "Check for missing brackets, parentheses, or braces",
                            "Verify proper string quotation",
                            "Check for missing semicolons",
                            "Ensure proper function syntax"
                        ]
                    }
                },
                'runtime_errors': {
                    'TypeError': {
                        'pattern': r"Cannot read property '([^']*)' of (null|undefined)",
                        'solutions': [
                            "Check if object is defined before accessing properties",
                            "Use optional chaining: object?.property",
                            "Add null/undefined checks",
                            "Initialize objects properly"
                        ],
                        'code_fix': '''
// Safe property access
const value = object?.{property} || defaultValue;

// Or explicit checking
if (object && object.{property}) {
    const value = object.{property};
}
                        '''
                    },
                    'ReferenceError': {
                        'pattern': r"([^ ]*) is not defined",
                        'solutions': [
                            "Declare variable before use",
                            "Check for typos in variable names",
                            "Ensure proper scope",
                            "Import required modules"
                        ]
                    }
                },
                'react_errors': {
                    'Warning: Each child in a list should have a unique "key" prop': {
                        'pattern': r"Each child.*unique.*key.*prop",
                        'solutions': [
                            "Add unique key prop to list items",
                            "Use item.id or index as key",
                            "Ensure keys are stable across renders"
                        ],
                        'code_fix': '''
// Fix missing keys in React lists
{items.map((item, index) => (
  <div key={item.id || index}>
    {item.content}
  </div>
))}
                        '''
                    },
                    'Warning: Hook called conditionally': {
                        'pattern': r"Hook.*called.*conditionally",
                        'solutions': [
                            "Move hooks to top level of component",
                            "Don't call hooks inside loops or conditions",
                            "Use conditional logic inside hooks"
                        ]
                    }
                }
            },
            'css': {
                'layout_issues': {
                    'flex_problems': {
                        'pattern': r"flexbox.*not.*working",
                        'solutions': [
                            "Set display: flex on parent container",
                            "Check flex-direction property",
                            "Use align-items and justify-content",
                            "Ensure flex items have proper flex properties"
                        ]
                    },
                    'grid_problems': {
                        'pattern': r"grid.*layout.*broken",
                        'solutions': [
                            "Set display: grid on container",
                            "Define grid-template-columns/rows",
                            "Check grid-area assignments",
                            "Use grid-gap for spacing"
                        ]
                    }
                }
            }
        }
    
    def auto_diagnose_error(self, error_message: str, code_context: str, 
                           language: str, file_path: str = "") -> Dict:
        """
        Automatically diagnose error and provide comprehensive solutions
        """
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        start_time = datetime.now()
        
        diagnosis = {
            'session_id': session_id,
            'error_type': 'unknown',
            'confidence': 0.0,
            'solutions': [],
            'code_fixes': [],
            'prevention_tips': [],
            'related_issues': [],
            'estimated_fix_time': 'unknown'
        }
        
        # Get language-specific patterns
        lang_patterns = self.troubleshooting_patterns.get(language.lower(), {})
        
        # Match error patterns
        best_match = None
        highest_confidence = 0.0
        
        for category, errors in lang_patterns.items():
            for error_type, error_data in errors.items():
                pattern = error_data.get('pattern', '')
                if pattern and re.search(pattern, error_message, re.IGNORECASE):
                    confidence = self._calculate_pattern_confidence(
                        pattern, error_message, code_context
                    )
                    if confidence > highest_confidence:
                        highest_confidence = confidence
                        best_match = (category, error_type, error_data)
        
        # Generate diagnosis based on best match
        if best_match:
            category, error_type, error_data = best_match
            diagnosis['error_type'] = error_type
            diagnosis['confidence'] = highest_confidence
            diagnosis['solutions'] = error_data.get('solutions', [])
            diagnosis['code_fixes'] = self._generate_specific_fixes(
                error_message, error_data, code_context
            )
            diagnosis['prevention_tips'] = self._get_prevention_tips(
                error_type, language
            )
            diagnosis['estimated_fix_time'] = self._estimate_fix_time(error_type)
        
        # Add contextual analysis
        diagnosis['related_issues'] = self._find_related_issues(
            error_message, code_context, language
        )
        
        # Log troubleshooting session
        duration = (datetime.now() - start_time).total_seconds()
        self._log_troubleshooting_session(
            session_id, error_message, language, diagnosis, duration
        )
        
        return diagnosis
    
    def _calculate_pattern_confidence(self, pattern: str, error_message: str, 
                                    code_context: str) -> float:
        """Calculate confidence score for pattern match"""
        base_confidence = 0.7 if re.search(pattern, error_message, re.IGNORECASE) else 0.0
        
        # Boost confidence based on context
        if code_context:
            context_keywords = self._extract_keywords_from_context(code_context)
            if any(keyword in error_message.lower() for keyword in context_keywords):
                base_confidence += 0.2
        
        return min(base_confidence, 1.0)
    
    def _generate_specific_fixes(self, error_message: str, error_data: Dict, 
                               code_context: str) -> List[str]:
        """Generate specific code fixes based on error analysis"""
        fixes = []
        base_fix = error_data.get('code_fix', '')
        
        if base_fix:
            # Extract specific details from error message
            details = self._extract_error_details(error_message)
            
            # Customize fix with specific details
            customized_fix = base_fix
            for key, value in details.items():
                customized_fix = customized_fix.replace(f'{{{key}}}', value)
            
            fixes.append(customized_fix)
        
        # Add context-specific fixes
        context_fixes = self._generate_context_specific_fixes(
            error_message, code_context
        )
        fixes.extend(context_fixes)
        
        return fixes
    
    def _extract_error_details(self, error_message: str) -> Dict[str, str]:
        """Extract specific details from error message"""
        details = {}
        
        # Extract module names
        module_match = re.search(r"No module named '([^']*)'", error_message)
        if module_match:
            details['module'] = module_match.group(1)
        
        # Extract key names
        key_match = re.search(r"KeyError: '([^']*)'", error_message)
        if key_match:
            details['key'] = key_match.group(1)
        
        # Extract property names
        prop_match = re.search(r"Cannot read property '([^']*)'", error_message)
        if prop_match:
            details['property'] = prop_match.group(1)
        
        return details
    
    def _generate_context_specific_fixes(self, error_message: str, 
                                       code_context: str) -> List[str]:
        """Generate fixes based on code context"""
        fixes = []
        
        if 'import' in error_message and 'requirements.txt' in code_context:
            fixes.append("Add the missing package to requirements.txt")
        
        if 'KeyError' in error_message and 'json' in code_context.lower():
            fixes.append("Check JSON structure and validate expected keys")
        
        if 'undefined' in error_message and 'fetch' in code_context:
            fixes.append("Add error handling for API response")
        
        return fixes
    
    def _get_prevention_tips(self, error_type: str, language: str) -> List[str]:
        """Get prevention tips for specific error types"""
        prevention_tips = {
            'ModuleNotFoundError': [
                "Use virtual environments to manage dependencies",
                "Keep requirements.txt updated",
                "Document installation steps clearly"
            ],
            'KeyError': [
                "Always validate data structure before accessing",
                "Use defensive programming with .get() method",
                "Add comprehensive error handling"
            ],
            'TypeError': [
                "Add type hints to functions",
                "Validate input types at function entry",
                "Use isinstance() for type checking"
            ],
            'SyntaxError': [
                "Use code linters and formatters",
                "Set up IDE with syntax highlighting",
                "Practice consistent coding style"
            ]
        }
        
        return prevention_tips.get(error_type, [
            "Follow best practices for the language",
            "Use proper error handling",
            "Write comprehensive tests"
        ])
    
    def _estimate_fix_time(self, error_type: str) -> str:
        """Estimate time needed to fix the error"""
        time_estimates = {
            'SyntaxError': '1-5 minutes',
            'ModuleNotFoundError': '1-3 minutes',
            'KeyError': '5-15 minutes',
            'TypeError': '10-30 minutes',
            'ImportError': '5-20 minutes',
            'ReferenceError': '2-10 minutes'
        }
        
        return time_estimates.get(error_type, '10-30 minutes')
    
    def _find_related_issues(self, error_message: str, code_context: str, 
                           language: str) -> List[str]:
        """Find potentially related issues in the code"""
        related_issues = []
        
        # Check for common patterns that might cause related issues
        if 'import' in error_message:
            if 'requirements.txt' not in code_context:
                related_issues.append("Missing requirements.txt file")
            if 'virtual environment' not in code_context:
                related_issues.append("Not using virtual environment")
        
        if 'undefined' in error_message and language == 'javascript':
            if 'const' not in code_context and 'let' not in code_context:
                related_issues.append("Using var instead of const/let")
        
        return related_issues
    
    def _extract_keywords_from_context(self, code_context: str) -> List[str]:
        """Extract relevant keywords from code context"""
        # Simple keyword extraction - could be enhanced with NLP
        keywords = []
        
        # Extract function names
        func_matches = re.findall(r'def\s+(\w+)', code_context)
        keywords.extend(func_matches)
        
        # Extract variable names
        var_matches = re.findall(r'(\w+)\s*=', code_context)
        keywords.extend(var_matches)
        
        return keywords
    
    def _log_troubleshooting_session(self, session_id: str, error_message: str, 
                                   language: str, diagnosis: Dict, duration: float):
        """Log troubleshooting session for learning"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO troubleshooting_sessions 
                (session_id, original_error, language, steps_taken, 
                 final_solution, success, duration_seconds)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                session_id, error_message, language,
                json.dumps(diagnosis['solutions']),
                json.dumps(diagnosis['code_fixes']),
                diagnosis['confidence'] > 0.5,
                duration
            ))
            conn.commit()
    
    def apply_automatic_fix(self, diagnosis: Dict, file_path: str, 
                          language: str) -> Dict:
        """
        Automatically apply fixes when confidence is high enough
        """
        result = {
            'applied': False,
            'fixes_applied': [],
            'backup_created': False,
            'success': False,
            'error': None
        }
        
        if diagnosis['confidence'] < 0.8:
            result['error'] = "Confidence too low for automatic fixing"
            return result
        
        try:
            # Create backup
            if file_path and os.path.exists(file_path):
                backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                with open(file_path, 'r') as f:
                    content = f.read()
                with open(backup_path, 'w') as f:
                    f.write(content)
                result['backup_created'] = True
            
            # Apply fixes based on error type
            for fix in diagnosis['code_fixes']:
                if self._is_safe_automatic_fix(fix, language):
                    applied = self._apply_code_fix(fix, file_path, language)
                    if applied:
                        result['fixes_applied'].append(fix)
            
            result['applied'] = len(result['fixes_applied']) > 0
            result['success'] = True
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def _is_safe_automatic_fix(self, fix: str, language: str) -> bool:
        """Check if fix is safe to apply automatically"""
        # Only apply simple, safe fixes automatically
        safe_patterns = [
            'pip install',  # Package installation
            'import ',      # Adding imports
            '.get(',        # Dictionary safe access
            'key in ',      # Key existence check
        ]
        
        return any(pattern in fix for pattern in safe_patterns)
    
    def _apply_code_fix(self, fix: str, file_path: str, language: str) -> bool:
        """Apply specific code fix to file"""
        try:
            if fix.startswith('pip install'):
                # Execute pip install command
                package = fix.replace('pip install ', '').strip()
                subprocess.run(['pip', 'install', package], check=True)
                return True
            
            # For other fixes, would need more sophisticated code modification
            # This is a placeholder for the actual implementation
            return False
            
        except Exception as e:
            logger.error(f"Failed to apply fix: {str(e)}")
            return False
    
    def learn_from_success(self, session_id: str, was_successful: bool, 
                          user_feedback: str = ""):
        """Learn from troubleshooting success/failure"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Update session success
            cursor.execute('''
                UPDATE troubleshooting_sessions 
                SET success = ? 
                WHERE session_id = ?
            ''', (was_successful, session_id))
            
            # Store feedback
            if user_feedback:
                effectiveness = 1.0 if was_successful else 0.0
                cursor.execute('''
                    INSERT INTO troubleshooting_feedback 
                    (session_id, feedback_type, feedback_content, effectiveness_score)
                    VALUES (?, ?, ?, ?)
                ''', (session_id, 'user_feedback', user_feedback, effectiveness))
            
            conn.commit()
    
    def get_troubleshooting_insights(self) -> Dict:
        """Get insights about troubleshooting performance"""
        insights = {
            'total_sessions': 0,
            'success_rate': 0.0,
            'common_errors': [],
            'improvement_areas': []
        }
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total sessions
            cursor.execute('SELECT COUNT(*) FROM troubleshooting_sessions')
            insights['total_sessions'] = cursor.fetchone()[0]
            
            # Success rate
            cursor.execute('''
                SELECT AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END) 
                FROM troubleshooting_sessions
            ''')
            result = cursor.fetchone()
            if result and result[0]:
                insights['success_rate'] = result[0]
            
            # Common errors
            cursor.execute('''
                SELECT original_error, COUNT(*) as count
                FROM troubleshooting_sessions
                GROUP BY original_error
                ORDER BY count DESC
                LIMIT 5
            ''')
            insights['common_errors'] = [
                {'error': row[0], 'count': row[1]} 
                for row in cursor.fetchall()
            ]
        
        return insights

# Initialize self-troubleshooting system
troubleshooting_ai = SelfTroubleshootingAI()