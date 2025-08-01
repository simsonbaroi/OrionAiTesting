import logging
import random
import time
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Firebase integration
try:
    from external_integrations.firebase_connector import get_firebase_connector
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    logger.warning("Firebase connector not available")

class SimplePythonExpert:
    """
    A multi-language expert that provides responses and generates applications.
    Supports Python, HTML, CSS, JavaScript, and React development.
    """
    
    def __init__(self):
        self.model_name = "multi-language-expert"
        self.version = "2.0.0"
        self.responses_db = self._init_response_database()
        self.app_templates = self._init_app_templates()
        
        # Initialize Firebase connector if available
        self.firebase = None
        if FIREBASE_AVAILABLE:
            try:
                self.firebase = get_firebase_connector()
                logger.info("Firebase integration enabled")
            except Exception as e:
                logger.warning(f"Firebase initialization failed: {str(e)}")
        
        logger.info("Multi-Language Expert initialized successfully")
    
    def _init_response_database(self) -> Dict[str, str]:
        """Initialize a comprehensive response database for multiple programming languages"""
        return {
            # Python concepts
            "variables": "In Python, variables are created by assigning a value to a name. For example: `name = 'John'` creates a string variable, and `age = 25` creates an integer variable. Python is dynamically typed, so you don't need to declare the variable type explicitly.",
            
            "lists": "Python lists are ordered collections that can hold different data types. Create a list with square brackets: `my_list = [1, 2, 3, 'hello']`. You can access elements by index: `my_list[0]` returns the first element. Lists are mutable, meaning you can modify them after creation.",
            
            "functions": "Functions in Python are defined using the `def` keyword. Here's the basic syntax:\n\n```python\ndef function_name(parameters):\n    # function body\n    return result\n```\n\nExample:\n```python\ndef greet(name):\n    return f'Hello, {name}!'\n```",
            
            "loops": "Python has two main types of loops:\n\n1. **For loops** - iterate over sequences:\n```python\nfor item in [1, 2, 3]:\n    print(item)\n```\n\n2. **While loops** - repeat while condition is true:\n```python\nwhile x < 10:\n    x += 1\n```",
            
            "dictionaries": "Dictionaries store key-value pairs. Create them with curly braces:\n\n```python\nmy_dict = {'name': 'John', 'age': 30}\nprint(my_dict['name'])  # Access by key\nmy_dict['city'] = 'New York'  # Add new key-value pair\n```",
            
            "classes": "Classes define objects in Python:\n\n```python\nclass Person:\n    def __init__(self, name, age):\n        self.name = name\n        self.age = age\n    \n    def introduce(self):\n        return f'Hi, I am {self.name}'\n\nperson = Person('Alice', 25)\nprint(person.introduce())\n```",
            
            "import": "Import modules to use external code:\n\n```python\n# Import entire module\nimport math\nprint(math.pi)\n\n# Import specific functions\nfrom datetime import datetime\nnow = datetime.now()\n\n# Import with alias\nimport numpy as np\n```",
            
            "error handling": "Use try-except blocks to handle errors gracefully:\n\n```python\ntry:\n    result = 10 / 0\nexcept ZeroDivisionError:\n    print('Cannot divide by zero!')\nexcept Exception as e:\n    print(f'An error occurred: {e}')\nfinally:\n    print('This always executes')\n```",
            
            # HTML concepts
            "html": "HTML (HyperText Markup Language) structures web content:\n\n```html\n<!DOCTYPE html>\n<html>\n<head>\n    <title>My Page</title>\n</head>\n<body>\n    <h1>Welcome</h1>\n    <p>This is a paragraph.</p>\n    <a href='#'>This is a link</a>\n</body>\n</html>\n```",
            
            "html forms": "HTML forms collect user input:\n\n```html\n<form action='/submit' method='post'>\n    <input type='text' name='username' placeholder='Username'>\n    <input type='password' name='password' placeholder='Password'>\n    <button type='submit'>Submit</button>\n</form>\n```",
            
            # CSS concepts
            "css": "CSS (Cascading Style Sheets) styles HTML elements:\n\n```css\nbody {\n    font-family: Arial, sans-serif;\n    margin: 0;\n    padding: 20px;\n}\n\n.container {\n    max-width: 800px;\n    margin: 0 auto;\n}\n\n.button {\n    background-color: #007bff;\n    color: white;\n    padding: 10px 20px;\n    border: none;\n    border-radius: 4px;\n}\n```",
            
            "css flexbox": "Flexbox creates flexible layouts:\n\n```css\n.flex-container {\n    display: flex;\n    justify-content: space-between;\n    align-items: center;\n}\n\n.flex-item {\n    flex: 1;\n    margin: 10px;\n}\n```",
            
            "css grid": "CSS Grid creates 2D layouts:\n\n```css\n.grid-container {\n    display: grid;\n    grid-template-columns: 1fr 2fr 1fr;\n    gap: 20px;\n}\n\n.grid-item {\n    background-color: #f0f0f0;\n    padding: 20px;\n}\n```",
            
            # JavaScript concepts
            "javascript": "JavaScript adds interactivity to web pages:\n\n```javascript\n// Variables and functions\nconst message = 'Hello, World!';\nfunction greet(name) {\n    return `Hello, ${name}!`;\n}\n\n// DOM manipulation\ndocument.getElementById('myButton').addEventListener('click', function() {\n    alert('Button clicked!');\n});\n```",
            
            "javascript arrays": "JavaScript arrays store multiple values:\n\n```javascript\nconst fruits = ['apple', 'banana', 'orange'];\n\n// Add item\nfruits.push('grape');\n\n// Loop through array\nfruits.forEach(fruit => {\n    console.log(fruit);\n});\n\n// Filter array\nconst longNames = fruits.filter(fruit => fruit.length > 5);\n```",
            
            "javascript objects": "JavaScript objects store key-value pairs:\n\n```javascript\nconst person = {\n    name: 'John',\n    age: 30,\n    greet: function() {\n        return `Hi, I'm ${this.name}`;\n    }\n};\n\nconsole.log(person.greet());\n```",
            
            "fetch api": "Fetch API makes HTTP requests:\n\n```javascript\nfetch('/api/data')\n    .then(response => response.json())\n    .then(data => {\n        console.log('Success:', data);\n    })\n    .catch(error => {\n        console.error('Error:', error);\n    });\n```",
            
            # React concepts
            "react": "React builds user interfaces with components:\n\n```jsx\nimport React, { useState } from 'react';\n\nfunction App() {\n    const [count, setCount] = useState(0);\n    \n    return (\n        <div>\n            <h1>Count: {count}</h1>\n            <button onClick={() => setCount(count + 1)}>\n                Increment\n            </button>\n        </div>\n    );\n}\n\nexport default App;\n```",
            
            "react hooks": "React Hooks manage state and effects:\n\n```jsx\nimport React, { useState, useEffect } from 'react';\n\nfunction DataComponent() {\n    const [data, setData] = useState(null);\n    \n    useEffect(() => {\n        fetch('/api/data')\n            .then(res => res.json())\n            .then(setData);\n    }, []);\n    \n    return data ? <div>{data.message}</div> : <div>Loading...</div>;\n}\n```",
            
            "react components": "React components are reusable UI pieces:\n\n```jsx\nfunction Button({ onClick, children, variant = 'primary' }) {\n    return (\n        <button \n            className={`btn btn-${variant}`}\n            onClick={onClick}\n        >\n            {children}\n        </button>\n    );\n}\n\nfunction App() {\n    return (\n        <div>\n            <Button onClick={() => alert('Hello!')}>Click Me</Button>\n            <Button variant='secondary'>Cancel</Button>\n        </div>\n    );\n}\n```"
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
            
            # Check if this is an app generation request
            app_keywords = ['create app', 'make app', 'build app', 'generate app', 'create application', 'make application']
            app_types = ['todo', 'calculator', 'react', 'flask', 'api']
            
            if any(keyword in question_lower for keyword in app_keywords) or any(app_type in question_lower for app_type in app_types):
                # Detect app type from question
                detected_type = None
                if any(word in question_lower for word in ['todo', 'task', 'list']):
                    detected_type = 'todo'
                elif any(word in question_lower for word in ['calculator', 'calc', 'math']):
                    detected_type = 'calculator'
                elif any(word in question_lower for word in ['react', 'counter']):
                    detected_type = 'react'
                elif any(word in question_lower for word in ['flask', 'api', 'backend']):
                    detected_type = 'flask'
                
                if detected_type:
                    app_result = self.generate_app(detected_type)
                    if app_result['success']:
                        # Log app generation to Firebase
                        self._log_app_generation(app_result, detected_type)
                        return self._format_app_response(app_result)
                    else:
                        return app_result['message']
            
            # Find the best matching response for regular questions
            best_match = None
            best_score = 0
            
            for key, response in self.responses_db.items():
                # Simple keyword matching
                if key in question_lower:
                    score = question_lower.count(key)
                    if score > best_score:
                        best_score = score
                        best_match = response
            
            # If no direct match, provide a general help response
            if not best_match:
                if any(word in question_lower for word in ['help', 'learn', 'tutorial', 'beginner']):
                    best_match = self._get_general_help_response()
                elif any(word in question_lower for word in ['error', 'bug', 'problem', 'fix']):
                    best_match = self._get_debugging_help()
                else:
                    best_match = self._get_default_response(question)
            
            # Store interaction in Firebase if available
            if self.firebase:
                try:
                    interaction_data = {
                        'question': question,
                        'response_type': 'app_generation' if any(keyword in question.lower() for keyword in ['create', 'make', 'build', 'generate']) else 'q_and_a',
                        'model_version': self.version,
                        'response_length': len(best_match)
                    }
                    self.firebase.store_user_interaction(interaction_data)
                except Exception as e:
                    logger.warning(f"Failed to store interaction in Firebase: {str(e)}")
            
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
    
    def _format_app_response(self, app_result: Dict[str, Any]) -> str:
        """Format app generation result as a response"""
        response = f"🚀 I've created a {app_result['name']} for you!\n\n"
        response += f"**Description:** {app_result['description']}\n\n"
        response += f"**Technologies:** {', '.join(app_result['technologies'])}\n\n"
        response += "**Files to create:**\n"
        
        for filename, content in app_result['files'].items():
            response += f"📄 **{filename}**\n```{self._get_file_language(filename)}\n{content}\n```\n\n"
        
        response += f"**Setup Instructions:**\n{app_result['instructions']}"
        return response
    
    def _get_file_language(self, filename: str) -> str:
        """Get the appropriate language identifier for code blocks"""
        if filename.endswith('.html'):
            return 'html'
        elif filename.endswith('.css'):
            return 'css'
        elif filename.endswith('.js'):
            return 'javascript'
        elif filename.endswith('.py'):
            return 'python'
        elif filename.endswith('.json'):
            return 'json'
        elif filename.endswith('.md'):
            return 'markdown'
        else:
            return 'text'
    
    def generate_app(self, app_type: str, app_name: str = None) -> Dict[str, Any]:
        """Generate a complete application based on the requested type"""
        try:
            if app_type.lower() in ['todo', 'todo app', 'todo list']:
                return self._generate_todo_app(app_name or "Todo List App")
            elif app_type.lower() in ['calculator', 'calc']:
                return self._generate_calculator_app(app_name or "Calculator App")
            elif app_type.lower() in ['react', 'react app', 'counter']:
                return self._generate_react_counter_app(app_name or "React Counter App")
            elif app_type.lower() in ['flask', 'api', 'flask api', 'python api']:
                return self._generate_flask_api(app_name or "Flask API")
            else:
                return {
                    'success': False,
                    'message': f"I don't have a template for '{app_type}' yet. Available app types: todo, calculator, react counter, flask api"
                }
        except Exception as e:
            logger.error(f"Error generating app: {str(e)}")
            return {
                'success': False,
                'message': f"Error generating app: {str(e)}"
            }
    
    def _log_app_generation(self, app_result: Dict[str, Any], app_type: str):
        """Log app generation to Firebase if available"""
        if self.firebase and app_result.get('success'):
            try:
                app_data = {
                    'app_type': app_type,
                    'app_name': app_result.get('name', 'Unknown'),
                    'technologies': app_result.get('technologies', []),
                    'file_count': len(app_result.get('files', {})),
                    'model_version': self.version
                }
                self.firebase.store_generated_app(app_data)
            except Exception as e:
                logger.warning(f"Failed to log app generation to Firebase: {str(e)}")
    
    def _generate_todo_app(self, name: str) -> Dict[str, Any]:
        """Generate a complete todo list application"""
        return {
            'success': True,
            'app_type': 'todo_app',
            'name': name,
            'description': 'A complete todo list app with HTML, CSS, and JavaScript',
            'technologies': ['HTML', 'CSS', 'JavaScript'],
            'files': {
                'index.html': self._get_todo_html(),
                'style.css': self._get_todo_css(),
                'script.js': self._get_todo_js()
            },
            'instructions': """
1. Save each file with the exact filename shown
2. Open index.html in a web browser
3. Start adding tasks to your todo list!

Features:
- Add new tasks
- Mark tasks as complete
- Delete tasks
- Data persists in browser storage
"""
        }
    
    def _generate_calculator_app(self, name: str) -> Dict[str, Any]:
        """Generate a calculator application"""
        return {
            'success': True,
            'app_type': 'calculator',
            'name': name,
            'description': 'A functional calculator with HTML, CSS, and JavaScript',
            'technologies': ['HTML', 'CSS', 'JavaScript'],
            'files': {
                'index.html': self._get_calculator_html(),
                'style.css': self._get_calculator_css(),
                'script.js': self._get_calculator_js()
            },
            'instructions': """
1. Save each file with the exact filename shown
2. Open index.html in a web browser
3. Use the calculator for basic math operations!

Features:
- Basic arithmetic operations (+, -, ×, ÷)
- Clear and backspace functions
- Responsive design
- Error handling for division by zero
"""
        }
    
    def _generate_react_counter_app(self, name: str) -> Dict[str, Any]:
        """Generate a React counter application"""
        return {
            'success': True,
            'app_type': 'react_app',
            'name': name,
            'description': 'A React application with counter functionality',
            'technologies': ['React', 'CSS', 'JavaScript'],
            'files': {
                'App.js': self._get_react_app_js(),
                'App.css': self._get_react_app_css(),
                'index.js': self._get_react_index_js(),
                'package.json': self._get_react_package_json()
            },
            'instructions': """
1. Make sure you have Node.js installed
2. Save all files in a new directory
3. Run: npm install
4. Run: npm start
5. Open http://localhost:3000 in your browser

Features:
- Increment/decrement counter
- Reset functionality
- View counter history
- Responsive design
"""
        }
    
    def _generate_flask_api(self, name: str) -> Dict[str, Any]:
        """Generate a Flask REST API"""
        return {
            'success': True,
            'app_type': 'flask_api',
            'name': name,
            'description': 'A complete Flask REST API with CRUD operations',
            'technologies': ['Python', 'Flask', 'SQLAlchemy'],
            'files': {
                'app.py': self._get_flask_app_py(),
                'requirements.txt': self._get_flask_requirements(),
                'README.md': self._get_flask_readme()
            },
            'instructions': """
1. Make sure you have Python installed
2. Save all files in a new directory
3. Run: pip install -r requirements.txt
4. Run: python app.py
5. API will be available at http://localhost:5000

Features:
- Full CRUD operations for tasks
- SQLite database with SQLAlchemy
- JSON API responses
- Error handling
- Health check endpoint
"""
        }
    
    def _init_app_templates(self) -> Dict[str, Dict[str, str]]:
        """Initialize templates for different types of applications"""
        return {
            "todo_app": {
                "name": "Todo List Application",
                "description": "A complete todo list app with HTML, CSS, and JavaScript",
                "files": {
                    "index.html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Todo List App</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <h1>My Todo List</h1>
        <div class="input-section">
            <input type="text" id="todoInput" placeholder="Add a new task...">
            <button id="addBtn">Add Task</button>
        </div>
        <ul id="todoList"></ul>
    </div>
    <script src="script.js"></script>
</body>
</html>""",
                    "style.css": """* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Arial', sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    padding: 20px;
}

.container {
    max-width: 600px;
    margin: 0 auto;
    background: white;
    border-radius: 10px;
    padding: 30px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}

h1 {
    text-align: center;
    color: #333;
    margin-bottom: 30px;
}

.input-section {
    display: flex;
    gap: 10px;
    margin-bottom: 30px;
}

#todoInput {
    flex: 1;
    padding: 12px;
    border: 2px solid #ddd;
    border-radius: 5px;
    font-size: 16px;
}

#addBtn {
    padding: 12px 20px;
    background: #667eea;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-size: 16px;
}

#addBtn:hover {
    background: #5a6fd8;
}

#todoList {
    list-style: none;
}

.todo-item {
    display: flex;
    align-items: center;
    padding: 15px;
    background: #f8f9fa;
    margin-bottom: 10px;
    border-radius: 5px;
    border-left: 4px solid #667eea;
}

.todo-item.completed {
    text-decoration: line-through;
    opacity: 0.6;
    border-left-color: #28a745;
}

.todo-text {
    flex: 1;
    margin-left: 10px;
}

.delete-btn {
    background: #dc3545;
    color: white;
    border: none;
    padding: 5px 10px;
    border-radius: 3px;
    cursor: pointer;
}""",
                    "script.js": """class TodoApp {
    constructor() {
        this.todos = JSON.parse(localStorage.getItem('todos')) || [];
        this.todoInput = document.getElementById('todoInput');
        this.addBtn = document.getElementById('addBtn');
        this.todoList = document.getElementById('todoList');
        
        this.init();
    }
    
    init() {
        this.addBtn.addEventListener('click', () => this.addTodo());
        this.todoInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.addTodo();
        });
        
        this.renderTodos();
    }
    
    addTodo() {
        const text = this.todoInput.value.trim();
        if (!text) return;
        
        const todo = {
            id: Date.now(),
            text: text,
            completed: false
        };
        
        this.todos.push(todo);
        this.todoInput.value = '';
        this.saveTodos();
        this.renderTodos();
    }
    
    toggleTodo(id) {
        this.todos = this.todos.map(todo =>
            todo.id === id ? { ...todo, completed: !todo.completed } : todo
        );
        this.saveTodos();
        this.renderTodos();
    }
    
    deleteTodo(id) {
        this.todos = this.todos.filter(todo => todo.id !== id);
        this.saveTodos();
        this.renderTodos();
    }
    
    renderTodos() {
        this.todoList.innerHTML = '';
        
        this.todos.forEach(todo => {
            const li = document.createElement('li');
            li.className = `todo-item ${todo.completed ? 'completed' : ''}`;
            
            li.innerHTML = `
                <input type="checkbox" ${todo.completed ? 'checked' : ''} 
                       onchange="app.toggleTodo(${todo.id})">
                <span class="todo-text">${todo.text}</span>
                <button class="delete-btn" onclick="app.deleteTodo(${todo.id})">Delete</button>
            `;
            
            this.todoList.appendChild(li);
        });
    }
    
    saveTodos() {
        localStorage.setItem('todos', JSON.stringify(this.todos));
    }
}

const app = new TodoApp();"""
                }
            },
            "calculator": {
                "name": "Calculator Application",
                "description": "A functional calculator with HTML, CSS, and JavaScript",
                "files": {
                    "index.html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Calculator</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="calculator">
        <div class="display">
            <input type="text" id="result" readonly>
        </div>
        <div class="buttons">
            <button onclick="clearDisplay()" class="operator">C</button>
            <button onclick="deleteLast()" class="operator">⌫</button>
            <button onclick="appendToDisplay('/')" class="operator">÷</button>
            <button onclick="appendToDisplay('*')" class="operator">×</button>
            
            <button onclick="appendToDisplay('7')">7</button>
            <button onclick="appendToDisplay('8')">8</button>
            <button onclick="appendToDisplay('9')">9</button>
            <button onclick="appendToDisplay('-')" class="operator">-</button>
            
            <button onclick="appendToDisplay('4')">4</button>
            <button onclick="appendToDisplay('5')">5</button>
            <button onclick="appendToDisplay('6')">6</button>
            <button onclick="appendToDisplay('+')" class="operator">+</button>
            
            <button onclick="appendToDisplay('1')">1</button>
            <button onclick="appendToDisplay('2')">2</button>
            <button onclick="appendToDisplay('3')">3</button>
            <button onclick="calculate()" class="equals" rowspan="2">=</button>
            
            <button onclick="appendToDisplay('0')" class="zero">0</button>
            <button onclick="appendToDisplay('.')">.</button>
        </div>
    </div>
    <script src="script.js"></script>
</body>
</html>""",
                    "style.css": """* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    background: linear-gradient(135deg, #1e3c72, #2a5298);
    font-family: Arial, sans-serif;
}

.calculator {
    background: #333;
    border-radius: 20px;
    padding: 20px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
}

.display {
    margin-bottom: 15px;
}

#result {
    width: 100%;
    height: 80px;
    font-size: 24px;
    text-align: right;
    padding: 0 15px;
    border: none;
    border-radius: 10px;
    background: #000;
    color: white;
    outline: none;
}

.buttons {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
}

button {
    height: 60px;
    border: none;
    border-radius: 10px;
    font-size: 20px;
    cursor: pointer;
    transition: all 0.2s;
}

button:hover {
    transform: scale(1.05);
}

button:active {
    transform: scale(0.95);
}

.operator {
    background: #ff9500;
    color: white;
}

.equals {
    background: #ff9500;
    color: white;
    grid-row: span 2;
}

.zero {
    grid-column: span 2;
}

button:not(.operator):not(.equals) {
    background: #505050;
    color: white;
}""",
                    "script.js": """let currentInput = '';
let operator = '';
let previousInput = '';

function appendToDisplay(value) {
    const display = document.getElementById('result');
    
    if (value === '.' && currentInput.includes('.')) {
        return; // Prevent multiple decimal points
    }
    
    currentInput += value;
    display.value = currentInput;
}

function clearDisplay() {
    currentInput = '';
    operator = '';
    previousInput = '';
    document.getElementById('result').value = '';
}

function deleteLast() {
    currentInput = currentInput.slice(0, -1);
    document.getElementById('result').value = currentInput;
}

function calculate() {
    if (currentInput === '' || operator === '' || previousInput === '') {
        return;
    }
    
    try {
        let result;
        const prev = parseFloat(previousInput);
        const current = parseFloat(currentInput);
        
        switch (operator) {
            case '+':
                result = prev + current;
                break;
            case '-':
                result = prev - current;
                break;
            case '*':
                result = prev * current;
                break;
            case '/':
                if (current === 0) {
                    alert('Cannot divide by zero!');
                    return;
                }
                result = prev / current;
                break;
            default:
                return;
        }
        
        document.getElementById('result').value = result;
        currentInput = result.toString();
        operator = '';
        previousInput = '';
        
    } catch (error) {
        alert('Error in calculation');
        clearDisplay();
    }
}

// Handle operators
document.addEventListener('DOMContentLoaded', function() {
    const operatorButtons = document.querySelectorAll('.operator');
    operatorButtons.forEach(button => {
        if (button.textContent !== 'C' && button.textContent !== '⌫') {
            button.addEventListener('click', function() {
                if (currentInput === '') return;
                
                if (previousInput !== '' && operator !== '') {
                    calculate();
                }
                
                operator = this.textContent === '×' ? '*' : this.textContent === '÷' ? '/' : this.textContent;
                previousInput = currentInput;
                currentInput = '';
            });
        }
    });
});"""
                }
            },
            "react_counter": {
                "name": "React Counter App",
                "description": "A React application with counter functionality",
                "files": {
                    "App.js": """import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [count, setCount] = useState(0);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    setHistory(prev => [...prev, count]);
  }, [count]);

  const increment = () => setCount(count + 1);
  const decrement = () => setCount(count - 1);
  const reset = () => {
    setCount(0);
    setHistory([0]);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>React Counter App</h1>
        <div className="counter-container">
          <div className="counter-display">
            <h2>Count: {count}</h2>
          </div>
          <div className="button-group">
            <button onClick={decrement} className="btn btn-danger">
              - Decrement
            </button>
            <button onClick={reset} className="btn btn-secondary">
              Reset
            </button>
            <button onClick={increment} className="btn btn-success">
              + Increment
            </button>
          </div>
        </div>
        <div className="history">
          <h3>History</h3>
          <div className="history-list">
            {history.slice(-10).map((value, index) => (
              <span key={index} className="history-item">
                {value}
              </span>
            ))}
          </div>
        </div>
      </header>
    </div>
  );
}

export default App;""",
                    "App.css": """.App {
  text-align: center;
}

.App-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
  padding: 20px;
  color: white;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.counter-container {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 40px;
  margin: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.counter-display h2 {
  font-size: 3rem;
  margin-bottom: 30px;
  font-weight: bold;
}

.button-group {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
  justify-content: center;
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 120px;
}

.btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.btn-success {
  background-color: #28a745;
  color: white;
}

.btn-danger {
  background-color: #dc3545;
  color: white;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.history {
  margin-top: 30px;
}

.history h3 {
  margin-bottom: 15px;
}

.history-list {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: center;
}

.history-item {
  background: rgba(255, 255, 255, 0.2);
  padding: 8px 12px;
  border-radius: 15px;
  font-weight: bold;
}

@media (max-width: 768px) {
  .counter-display h2 {
    font-size: 2rem;
  }
  
  .button-group {
    flex-direction: column;
    align-items: center;
  }
  
  .btn {
    width: 200px;
  }
}""",
                    "index.js": """import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);""",
                    "package.json": """{
  "name": "react-counter-app",
  "version": "1.0.0",
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  }
}"""
                }
            },
            "python_flask_api": {
                "name": "Python Flask API",
                "description": "A complete Flask REST API with CRUD operations",
                "files": {
                    "app.py": """from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///tasks.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Task model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'completed': self.completed,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

# Routes
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()
    return jsonify([task.to_dict() for task in tasks])

@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    
    if not data or not data.get('title'):
        return jsonify({'error': 'Title is required'}), 400
    
    task = Task(
        title=data['title'],
        description=data.get('description', '')
    )
    
    db.session.add(task)
    db.session.commit()
    
    return jsonify(task.to_dict()), 201

@app.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = Task.query.get_or_404(task_id)
    return jsonify(task.to_dict())

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json()
    
    if 'title' in data:
        task.title = data['title']
    if 'description' in data:
        task.description = data['description']
    if 'completed' in data:
        task.completed = data['completed']
    
    task.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify(task.to_dict())

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    
    return '', 204

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)""",
                    "requirements.txt": """Flask==2.3.3
Flask-SQLAlchemy==3.0.5
python-dotenv==1.0.0""",
                    "README.md": """# Flask Task API

A simple REST API built with Flask for managing tasks.

## Features

- Create, read, update, and delete tasks
- SQLite database with SQLAlchemy ORM
- JSON API responses
- Error handling

## Installation

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the application:
   ```
   python app.py
   ```

## API Endpoints

- `GET /api/tasks` - Get all tasks
- `POST /api/tasks` - Create a new task
- `GET /api/tasks/<id>` - Get a specific task
- `PUT /api/tasks/<id>` - Update a task
- `DELETE /api/tasks/<id>` - Delete a task
- `GET /health` - Health check

## Example Usage

```bash
# Create a task
curl -X POST http://localhost:5000/api/tasks \\
  -H "Content-Type: application/json" \\
  -d '{"title": "Learn Flask", "description": "Build a REST API"}'

# Get all tasks
curl http://localhost:5000/api/tasks

# Update a task
curl -X PUT http://localhost:5000/api/tasks/1 \\
  -H "Content-Type: application/json" \\
  -d '{"completed": true}'
```"""
                }
            }
        }
    
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
    
    def _get_todo_html(self) -> str:
        """Get HTML content for todo app"""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Todo List App</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <h1>My Todo List</h1>
        <div class="input-section">
            <input type="text" id="todoInput" placeholder="Add a new task...">
            <button id="addBtn">Add Task</button>
        </div>
        <ul id="todoList"></ul>
    </div>
    <script src="script.js"></script>
</body>
</html>"""
    
    def _get_todo_css(self) -> str:
        """Get CSS content for todo app"""
        return """* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Arial', sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    padding: 20px;
}

.container {
    max-width: 600px;
    margin: 0 auto;
    background: white;
    border-radius: 10px;
    padding: 30px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}

h1 {
    text-align: center;
    color: #333;
    margin-bottom: 30px;
}

.input-section {
    display: flex;
    gap: 10px;
    margin-bottom: 30px;
}

#todoInput {
    flex: 1;
    padding: 12px;
    border: 2px solid #ddd;
    border-radius: 5px;
    font-size: 16px;
}

#addBtn {
    padding: 12px 20px;
    background: #667eea;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-size: 16px;
}

#addBtn:hover {
    background: #5a6fd8;
}

#todoList {
    list-style: none;
}

.todo-item {
    display: flex;
    align-items: center;
    padding: 15px;
    background: #f8f9fa;
    margin-bottom: 10px;
    border-radius: 5px;
    border-left: 4px solid #667eea;
}

.todo-item.completed {
    text-decoration: line-through;
    opacity: 0.6;
    border-left-color: #28a745;
}

.todo-text {
    flex: 1;
    margin-left: 10px;
}

.delete-btn {
    background: #dc3545;
    color: white;
    border: none;
    padding: 5px 10px;
    border-radius: 3px;
    cursor: pointer;
}"""
    
    def _get_todo_js(self) -> str:
        """Get JavaScript content for todo app"""
        return """class TodoApp {
    constructor() {
        this.todos = JSON.parse(localStorage.getItem('todos')) || [];
        this.todoInput = document.getElementById('todoInput');
        this.addBtn = document.getElementById('addBtn');
        this.todoList = document.getElementById('todoList');
        
        this.init();
    }
    
    init() {
        this.addBtn.addEventListener('click', () => this.addTodo());
        this.todoInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.addTodo();
        });
        
        this.renderTodos();
    }
    
    addTodo() {
        const text = this.todoInput.value.trim();
        if (!text) return;
        
        const todo = {
            id: Date.now(),
            text: text,
            completed: false
        };
        
        this.todos.push(todo);
        this.todoInput.value = '';
        this.saveTodos();
        this.renderTodos();
    }
    
    toggleTodo(id) {
        this.todos = this.todos.map(todo =>
            todo.id === id ? { ...todo, completed: !todo.completed } : todo
        );
        this.saveTodos();
        this.renderTodos();
    }
    
    deleteTodo(id) {
        this.todos = this.todos.filter(todo => todo.id !== id);
        this.saveTodos();
        this.renderTodos();
    }
    
    renderTodos() {
        this.todoList.innerHTML = '';
        
        this.todos.forEach(todo => {
            const li = document.createElement('li');
            li.className = `todo-item ${todo.completed ? 'completed' : ''}`;
            
            li.innerHTML = `
                <input type="checkbox" ${todo.completed ? 'checked' : ''} 
                       onchange="app.toggleTodo(${todo.id})">
                <span class="todo-text">${todo.text}</span>
                <button class="delete-btn" onclick="app.deleteTodo(${todo.id})">Delete</button>
            `;
            
            this.todoList.appendChild(li);
        });
    }
    
    saveTodos() {
        localStorage.setItem('todos', JSON.stringify(this.todos));
    }
}

const app = new TodoApp();"""
    
    def _get_calculator_html(self) -> str:
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Calculator</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="calculator">
        <div class="display">
            <input type="text" id="result" readonly>
        </div>
        <div class="buttons">
            <button onclick="clearDisplay()" class="operator">C</button>
            <button onclick="deleteLast()" class="operator">⌫</button>
            <button onclick="appendToDisplay('/')" class="operator">÷</button>
            <button onclick="appendToDisplay('*')" class="operator">×</button>
            
            <button onclick="appendToDisplay('7')">7</button>
            <button onclick="appendToDisplay('8')">8</button>
            <button onclick="appendToDisplay('9')">9</button>
            <button onclick="appendToDisplay('-')" class="operator">-</button>
            
            <button onclick="appendToDisplay('4')">4</button>
            <button onclick="appendToDisplay('5')">5</button>
            <button onclick="appendToDisplay('6')">6</button>
            <button onclick="appendToDisplay('+')" class="operator">+</button>
            
            <button onclick="appendToDisplay('1')">1</button>
            <button onclick="appendToDisplay('2')">2</button>
            <button onclick="appendToDisplay('3')">3</button>
            <button onclick="calculate()" class="equals" rowspan="2">=</button>
            
            <button onclick="appendToDisplay('0')" class="zero">0</button>
            <button onclick="appendToDisplay('.')">.</button>
        </div>
    </div>
    <script src="script.js"></script>
</body>
</html>"""
    
    def _get_calculator_css(self) -> str:
        return """* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    background: linear-gradient(135deg, #1e3c72, #2a5298);
    font-family: Arial, sans-serif;
}

.calculator {
    background: #333;
    border-radius: 20px;
    padding: 20px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
}

.display {
    margin-bottom: 15px;
}

#result {
    width: 100%;
    height: 80px;
    font-size: 24px;
    text-align: right;
    padding: 0 15px;
    border: none;
    border-radius: 10px;
    background: #000;
    color: white;
    outline: none;
}

.buttons {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
}

button {
    height: 60px;
    border: none;
    border-radius: 10px;
    font-size: 20px;
    cursor: pointer;
    transition: all 0.2s;
}

button:hover {
    transform: scale(1.05);
}

button:active {
    transform: scale(0.95);
}

.operator {
    background: #ff9500;
    color: white;
}

.equals {
    background: #ff9500;
    color: white;
    grid-row: span 2;
}

.zero {
    grid-column: span 2;
}

button:not(.operator):not(.equals) {
    background: #505050;
    color: white;
}"""
    
    def _get_calculator_js(self) -> str:
        return """let currentInput = '';
let operator = '';
let previousInput = '';

function appendToDisplay(value) {
    const display = document.getElementById('result');
    
    if (value === '.' && currentInput.includes('.')) {
        return;
    }
    
    currentInput += value;
    display.value = currentInput;
}

function clearDisplay() {
    currentInput = '';
    operator = '';
    previousInput = '';
    document.getElementById('result').value = '';
}

function deleteLast() {
    currentInput = currentInput.slice(0, -1);
    document.getElementById('result').value = currentInput;
}

function calculate() {
    if (currentInput === '' || operator === '' || previousInput === '') {
        return;
    }
    
    try {
        let result;
        const prev = parseFloat(previousInput);
        const current = parseFloat(currentInput);
        
        switch (operator) {
            case '+':
                result = prev + current;
                break;
            case '-':
                result = prev - current;
                break;
            case '*':
                result = prev * current;
                break;
            case '/':
                if (current === 0) {
                    alert('Cannot divide by zero!');
                    return;
                }
                result = prev / current;
                break;
            default:
                return;
        }
        
        document.getElementById('result').value = result;
        currentInput = result.toString();
        operator = '';
        previousInput = '';
        
    } catch (error) {
        alert('Error in calculation');
        clearDisplay();
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const operatorButtons = document.querySelectorAll('.operator');
    operatorButtons.forEach(button => {
        if (button.textContent !== 'C' && button.textContent !== '⌫') {
            button.addEventListener('click', function() {
                if (currentInput === '') return;
                
                if (previousInput !== '' && operator !== '') {
                    calculate();
                }
                
                operator = this.textContent === '×' ? '*' : this.textContent === '÷' ? '/' : this.textContent;
                previousInput = currentInput;
                currentInput = '';
            });
        }
    });
});"""
    
    def _get_react_app_js(self) -> str:
        return """import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [count, setCount] = useState(0);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    setHistory(prev => [...prev, count]);
  }, [count]);

  const increment = () => setCount(count + 1);
  const decrement = () => setCount(count - 1);
  const reset = () => {
    setCount(0);
    setHistory([0]);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>React Counter App</h1>
        <div className="counter-container">
          <div className="counter-display">
            <h2>Count: {count}</h2>
          </div>
          <div className="button-group">
            <button onClick={decrement} className="btn btn-danger">
              - Decrement
            </button>
            <button onClick={reset} className="btn btn-secondary">
              Reset
            </button>
            <button onClick={increment} className="btn btn-success">
              + Increment
            </button>
          </div>
        </div>
        <div className="history">
          <h3>History</h3>
          <div className="history-list">
            {history.slice(-10).map((value, index) => (
              <span key={index} className="history-item">
                {value}
              </span>
            ))}
          </div>
        </div>
      </header>
    </div>
  );
}

export default App;"""
    
    def _get_react_app_css(self) -> str:
        return """.App {
  text-align: center;
}

.App-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
  padding: 20px;
  color: white;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.counter-container {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 40px;
  margin: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.counter-display h2 {
  font-size: 3rem;
  margin-bottom: 30px;
  font-weight: bold;
}

.button-group {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
  justify-content: center;
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 120px;
}

.btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.btn-success {
  background-color: #28a745;
  color: white;
}

.btn-danger {
  background-color: #dc3545;
  color: white;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.history {
  margin-top: 30px;
}

.history h3 {
  margin-bottom: 15px;
}

.history-list {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: center;
}

.history-item {
  background: rgba(255, 255, 255, 0.2);
  padding: 8px 12px;
  border-radius: 15px;
  font-weight: bold;
}

@media (max-width: 768px) {
  .counter-display h2 {
    font-size: 2rem;
  }
  
  .button-group {
    flex-direction: column;
    align-items: center;
  }
  
  .btn {
    width: 200px;
  }
}"""
    
    def _get_react_index_js(self) -> str:
        return """import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);"""
    
    def _get_react_package_json(self) -> str:
        return """{
  "name": "react-counter-app",
  "version": "1.0.0",
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  }
}"""
    
    def _get_flask_app_py(self) -> str:
        return """from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///tasks.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'completed': self.completed,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()
    return jsonify([task.to_dict() for task in tasks])

@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    
    if not data or not data.get('title'):
        return jsonify({'error': 'Title is required'}), 400
    
    task = Task(
        title=data['title'],
        description=data.get('description', '')
    )
    
    db.session.add(task)
    db.session.commit()
    
    return jsonify(task.to_dict()), 201

@app.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = Task.query.get_or_404(task_id)
    return jsonify(task.to_dict())

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json()
    
    if 'title' in data:
        task.title = data['title']
    if 'description' in data:
        task.description = data['description']
    if 'completed' in data:
        task.completed = data['completed']
    
    task.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify(task.to_dict())

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    
    return '', 204

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)"""
    
    def _get_flask_requirements(self) -> str:
        return """Flask==2.3.3
Flask-SQLAlchemy==3.0.5
python-dotenv==1.0.0"""
    
    def _get_flask_readme(self) -> str:
        return """# Flask Task API

A simple REST API built with Flask for managing tasks.

## Features

- Create, read, update, and delete tasks
- SQLite database with SQLAlchemy ORM
- JSON API responses
- Error handling

## Installation

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the application:
   ```
   python app.py
   ```

## API Endpoints

- `GET /api/tasks` - Get all tasks
- `POST /api/tasks` - Create a new task
- `GET /api/tasks/<id>` - Get a specific task
- `PUT /api/tasks/<id>` - Update a task
- `DELETE /api/tasks/<id>` - Delete a task
- `GET /health` - Health check

## Example Usage

```bash
# Create a task
curl -X POST http://localhost:5000/api/tasks \\
  -H "Content-Type: application/json" \\
  -d '{"title": "Learn Flask", "description": "Build a REST API"}'

# Get all tasks
curl http://localhost:5000/api/tasks

# Update a task
curl -X PUT http://localhost:5000/api/tasks/1 \\
  -H "Content-Type: application/json" \\
  -d '{"completed": true}'
```"""