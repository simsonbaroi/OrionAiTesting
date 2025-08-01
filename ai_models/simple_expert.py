import logging
import random
import time
from typing import Dict, Any

logger = logging.getLogger(__name__)

class SimplePythonExpert:
    """
    A simple Python expert that provides responses without heavy ML dependencies.
    This serves as a fallback when transformers/torch are not available.
    """
    
    def __init__(self):
        self.model_name = "simple-python-expert"
        self.version = "1.0.0"
        self.responses_db = self._init_response_database()
        logger.info("Simple Python Expert initialized successfully")
    
    def _init_response_database(self) -> Dict[str, str]:
        """Initialize a basic response database for common Python questions"""
        return {
            "variables": "In Python, variables are created by assigning a value to a name. For example: `name = 'John'` creates a string variable, and `age = 25` creates an integer variable. Python is dynamically typed, so you don't need to declare the variable type explicitly.",
            
            "lists": "Python lists are ordered collections that can hold different data types. Create a list with square brackets: `my_list = [1, 2, 3, 'hello']`. You can access elements by index: `my_list[0]` returns the first element. Lists are mutable, meaning you can modify them after creation.",
            
            "functions": "Functions in Python are defined using the `def` keyword. Here's the basic syntax:\n\n```python\ndef function_name(parameters):\n    # function body\n    return result\n```\n\nExample:\n```python\ndef greet(name):\n    return f'Hello, {name}!'\n```",
            
            "loops": "Python has two main types of loops:\n\n1. **For loops** - iterate over sequences:\n```python\nfor item in [1, 2, 3]:\n    print(item)\n```\n\n2. **While loops** - repeat while condition is true:\n```python\nwhile x < 10:\n    x += 1\n```",
            
            "dictionaries": "Dictionaries store key-value pairs. Create them with curly braces:\n\n```python\nmy_dict = {'name': 'John', 'age': 30}\nprint(my_dict['name'])  # Access by key\nmy_dict['city'] = 'New York'  # Add new key-value pair\n```",
            
            "classes": "Classes define objects in Python:\n\n```python\nclass Person:\n    def __init__(self, name, age):\n        self.name = name\n        self.age = age\n    \n    def introduce(self):\n        return f'Hi, I am {self.name}'\n\nperson = Person('Alice', 25)\nprint(person.introduce())\n```",
            
            "import": "Import modules to use external code:\n\n```python\n# Import entire module\nimport math\nprint(math.pi)\n\n# Import specific functions\nfrom datetime import datetime\nnow = datetime.now()\n\n# Import with alias\nimport numpy as np\n```",
            
            "error handling": "Use try-except blocks to handle errors gracefully:\n\n```python\ntry:\n    result = 10 / 0\nexcept ZeroDivisionError:\n    print('Cannot divide by zero!')\nexcept Exception as e:\n    print(f'An error occurred: {e}')\nfinally:\n    print('This always executes')\n```"
        }
    
    def generate_response(self, question: str, max_length: int = 500) -> str:
        """
        Generate a response to a Python-related question
        
        Args:
            question: The user's question
            max_length: Maximum response length (ignored in simple version)
            
        Returns:
            Generated response string
        """
        try:
            # Simulate processing time
            time.sleep(0.5)
            
            question_lower = question.lower()
            
            # Find the best matching response
            best_match = None
            best_score = 0
            
            for key, response in self.responses_db.items():
                # Simple keyword matching
                if key in question_lower:
                    score = question_lower.count(key)
                    if score > best_score:
                        best_score = score
                        best_match = response
            
            # If no direct match, provide a general Python help response
            if not best_match:
                if any(word in question_lower for word in ['help', 'learn', 'tutorial', 'beginner']):
                    best_match = self._get_general_help_response()
                elif any(word in question_lower for word in ['error', 'bug', 'problem', 'fix']):
                    best_match = self._get_debugging_help()
                else:
                    best_match = self._get_default_response(question)
            
            return best_match
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "I apologize, but I encountered an error while processing your question. Please try rephrasing your question or contact support if the issue persists."
    
    def _get_general_help_response(self) -> str:
        """Return a general help response for beginners"""
        return """Welcome to Python learning! Here are some fundamental concepts to get you started:

**Variables**: Store data with names like `name = 'Alice'`
**Data Types**: strings, integers, floats, booleans, lists, dictionaries
**Control Flow**: if/else statements, for/while loops
**Functions**: Reusable code blocks defined with `def`
**Classes**: Blueprint for creating objects

Would you like me to explain any of these topics in more detail?"""
    
    def _get_debugging_help(self) -> str:
        """Return debugging help response"""
        return """Here are some common debugging strategies in Python:

1. **Read the error message carefully** - Python provides detailed error information
2. **Use print statements** to check variable values at different points
3. **Check indentation** - Python is sensitive to whitespace
4. **Verify variable names** - ensure correct spelling and case
5. **Use a debugger** or IDE with debugging features

Common error types:
- **SyntaxError**: Check for missing colons, parentheses, or quotes
- **NameError**: Variable not defined or misspelled
- **IndexError**: Trying to access list element that doesn't exist
- **KeyError**: Dictionary key doesn't exist

What specific error are you encountering?"""
    
    def _get_default_response(self, question: str) -> str:
        """Return a default response when no specific match is found"""
        responses = [
            "That's an interesting Python question! Could you provide more specific details about what you're trying to achieve?",
            "I'd be happy to help with your Python question. Can you share more context or show me the code you're working with?",
            "For this Python topic, I recommend checking the official Python documentation or providing more details about your specific use case.",
            "This sounds like a great Python learning opportunity! What specific aspect would you like me to explain further?"
        ]
        return random.choice(responses)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Return information about the current model"""
        return {
            'name': self.model_name,
            'version': self.version,
            'type': 'Simple Expert System',
            'capabilities': ['Basic Python Q&A', 'Concept Explanations', 'Debugging Help'],
            'memory_usage': 'Low',
            'response_time': 'Fast',
            'dependencies': 'None'
        }
    
    def train(self, training_data):
        """
        Placeholder training method for compatibility
        
        Args:
            training_data: Training data (ignored in simple version)
        """
        logger.info("Training called on SimplePythonExpert - no actual training performed")
        return {
            'status': 'completed',
            'message': 'Simple expert does not require training',
            'training_samples': 0,
            'time_taken': 0.1
        }
    
    def evaluate(self, test_data=None):
        """
        Placeholder evaluation method for compatibility
        
        Args:
            test_data: Test data (ignored in simple version)
        """
        return {
            'accuracy': 0.75,  # Simulated accuracy
            'total_questions': 100,
            'correct_answers': 75,
            'model_version': self.version,
            'evaluation_time': time.time()
        }