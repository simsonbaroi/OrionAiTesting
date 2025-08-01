#!/usr/bin/env python3
"""
Initialize the database with comprehensive multi-language learning content
"""

from app import app, db
from models import (
    KnowledgeBase, TrainingData, ProjectTemplate, CodeExample, 
    LearningPath, SystemConfig, ScrapingLog
)
from datetime import datetime
import json


def initialize_multi_language_database():
    """Populate database with comprehensive multi-language content"""
    
    with app.app_context():
        # Clear existing data (for fresh start)
        db.drop_all()
        db.create_all()
        
        print("🚀 Initializing PyLearnAI Multi-Language Database...")
        
        # Initialize Python Knowledge Base
        python_knowledge_items = [
            {
                'title': 'Python Functions and Parameters',
                'content': '''Functions in Python are defined using the `def` keyword and can accept parameters to make them flexible and reusable.

Basic syntax:
```python
def function_name(parameter1, parameter2):
    # Function body
    return result
```

Example:
```python
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"

# Usage
print(greet("Alice"))          # Hello, Alice!
print(greet("Bob", "Hi"))      # Hi, Bob!
```

Functions can have default parameters, variable-length arguments (*args), and keyword arguments (**kwargs).''',
                'language': 'python',
                'difficulty': 'beginner',
                'category': 'functions',
                'tags': ['functions', 'parameters', 'syntax'],
                'quality_score': 9.2,
                'source_type': 'python_docs'
            },
            {
                'title': 'Python Data Structures: Lists and Dictionaries',
                'content': '''Python provides powerful built-in data structures for organizing and manipulating data.

**Lists** - Ordered, mutable collections:
```python
# Creating and manipulating lists
fruits = ['apple', 'banana', 'orange']
fruits.append('grape')
fruits.insert(1, 'kiwi')
print(fruits[0])  # apple

# List comprehensions
squares = [x**2 for x in range(1, 6)]  # [1, 4, 9, 16, 25]
```

**Dictionaries** - Key-value pairs:
```python
# Creating and using dictionaries
person = {
    'name': 'John',
    'age': 30,
    'city': 'New York'
}

# Accessing and modifying
print(person['name'])  # John
person['email'] = 'john@example.com'

# Dictionary methods
keys = person.keys()
values = person.values()
```''',
                'language': 'python',
                'difficulty': 'beginner',
                'category': 'data-structures',
                'tags': ['lists', 'dictionaries', 'data-structures'],
                'quality_score': 9.5,
                'source_type': 'python_docs'
            },
            {
                'title': 'Object-Oriented Programming in Python',
                'content': '''Python supports object-oriented programming with classes and objects.

**Class Definition:**
```python
class Vehicle:
    def __init__(self, brand, model, year):
        self.brand = brand
        self.model = model
        self.year = year
        self.is_running = False
    
    def start(self):
        self.is_running = True
        return f"{self.brand} {self.model} is now running!"
    
    def stop(self):
        self.is_running = False
        return f"{self.brand} {self.model} has stopped."

# Creating objects
car = Vehicle("Toyota", "Camry", 2023)
print(car.start())  # Toyota Camry is now running!
```

**Inheritance:**
```python
class ElectricCar(Vehicle):
    def __init__(self, brand, model, year, battery_capacity):
        super().__init__(brand, model, year)
        self.battery_capacity = battery_capacity
    
    def charge(self):
        return f"Charging {self.brand} {self.model}..."
```''',
                'language': 'python',
                'difficulty': 'intermediate',
                'category': 'oop',
                'tags': ['classes', 'objects', 'inheritance', 'oop'],
                'quality_score': 9.8,
                'source_type': 'python_docs'
            }
        ]
        
        # Initialize JavaScript Knowledge Base
        javascript_knowledge_items = [
            {
                'title': 'JavaScript ES6+ Arrow Functions and Destructuring',
                'content': '''Modern JavaScript (ES6+) introduces concise syntax for functions and data manipulation.

**Arrow Functions:**
```javascript
// Traditional function
function add(a, b) {
    return a + b;
}

// Arrow function
const add = (a, b) => a + b;

// With multiple statements
const greet = (name) => {
    const message = `Hello, ${name}!`;
    return message;
};
```

**Destructuring:**
```javascript
// Array destructuring
const [first, second, ...rest] = [1, 2, 3, 4, 5];
console.log(first);  // 1
console.log(rest);   // [3, 4, 5]

// Object destructuring
const person = { name: 'Alice', age: 30, city: 'Boston' };
const { name, age } = person;
console.log(name);  // Alice

// Function parameter destructuring
const printPerson = ({ name, age }) => {
    console.log(`${name} is ${age} years old`);
};
```''',
                'language': 'javascript',
                'difficulty': 'intermediate',
                'category': 'syntax',
                'tags': ['es6', 'arrow-functions', 'destructuring'],
                'quality_score': 9.0,
                'source_type': 'javascript_docs'
            },
            {
                'title': 'JavaScript Async Programming: Promises and Async/Await',
                'content': '''Handle asynchronous operations in JavaScript using Promises and async/await.

**Promises:**
```javascript
// Creating a Promise
const fetchData = () => {
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            const data = { id: 1, name: 'User Data' };
            resolve(data);
        }, 1000);
    });
};

// Using Promises
fetchData()
    .then(data => console.log(data))
    .catch(error => console.error(error));
```

**Async/Await:**
```javascript
// Async function
async function getUserData(userId) {
    try {
        const response = await fetch(`/api/users/${userId}`);
        const userData = await response.json();
        return userData;
    } catch (error) {
        console.error('Error fetching user data:', error);
        throw error;
    }
}

// Using async function
(async () => {
    const user = await getUserData(123);
    console.log(user);
})();
```''',
                'language': 'javascript',
                'difficulty': 'intermediate',
                'category': 'async',
                'tags': ['promises', 'async-await', 'asynchronous'],
                'quality_score': 9.3,
                'source_type': 'javascript_docs'
            }
        ]
        
        # Initialize HTML Knowledge Base
        html_knowledge_items = [
            {
                'title': 'HTML5 Semantic Elements and Document Structure',
                'content': '''HTML5 introduces semantic elements that provide meaning to document structure.

**Basic Document Structure:**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Page Title</title>
</head>
<body>
    <header>
        <nav>
            <ul>
                <li><a href="#home">Home</a></li>
                <li><a href="#about">About</a></li>
            </ul>
        </nav>
    </header>
    
    <main>
        <section>
            <h1>Main Content</h1>
            <article>
                <h2>Article Title</h2>
                <p>Article content goes here...</p>
            </article>
        </section>
        
        <aside>
            <h3>Sidebar</h3>
            <p>Additional information</p>
        </aside>
    </main>
    
    <footer>
        <p>&copy; 2024 Website Name</p>
    </footer>
</body>
</html>
```

**Semantic Elements:**
- `<header>`: Page or section header
- `<nav>`: Navigation links
- `<main>`: Main content area
- `<section>`: Thematic grouping
- `<article>`: Independent content
- `<aside>`: Sidebar content
- `<footer>`: Page or section footer''',
                'language': 'html',
                'difficulty': 'beginner',
                'category': 'structure',
                'tags': ['html5', 'semantic', 'structure'],
                'quality_score': 9.1,
                'source_type': 'html_docs'
            }
        ]
        
        # Initialize CSS Knowledge Base
        css_knowledge_items = [
            {
                'title': 'CSS Flexbox Layout System',
                'content': '''Flexbox provides a powerful way to arrange elements in one dimension.

**Basic Flexbox Container:**
```css
.container {
    display: flex;
    justify-content: center;    /* Horizontal alignment */
    align-items: center;        /* Vertical alignment */
    gap: 20px;                  /* Space between items */
}

/* Flex direction options */
.row { flex-direction: row; }           /* Default */
.column { flex-direction: column; }
.row-reverse { flex-direction: row-reverse; }
```

**Flex Items:**
```css
.item {
    flex: 1;                    /* Grow to fill space */
    flex-basis: 200px;          /* Starting size */
    flex-shrink: 0;             /* Don't shrink */
    align-self: flex-start;     /* Individual alignment */
}

/* Common patterns */
.equal-width { flex: 1; }
.fixed-width { flex: 0 0 200px; }
.grow-only { flex: 1 0 auto; }
```

**Responsive Navigation:**
```css
.nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
}

.nav-links {
    display: flex;
    gap: 2rem;
    list-style: none;
}

@media (max-width: 768px) {
    .nav {
        flex-direction: column;
    }
}
```''',
                'language': 'css',
                'difficulty': 'intermediate',
                'category': 'layout',
                'tags': ['flexbox', 'layout', 'responsive'],
                'quality_score': 9.4,
                'source_type': 'css_docs'
            }
        ]
        
        # Initialize React Knowledge Base
        react_knowledge_items = [
            {
                'title': 'React Functional Components and Hooks',
                'content': '''Modern React development uses functional components with hooks for state management.

**Functional Component with useState:**
```jsx
import React, { useState, useEffect } from 'react';

const UserProfile = ({ userId }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    
    useEffect(() => {
        const fetchUser = async () => {
            try {
                const response = await fetch(`/api/users/${userId}`);
                const userData = await response.json();
                setUser(userData);
            } catch (error) {
                console.error('Error fetching user:', error);
            } finally {
                setLoading(false);
            }
        };
        
        fetchUser();
    }, [userId]);
    
    if (loading) return <div>Loading...</div>;
    if (!user) return <div>User not found</div>;
    
    return (
        <div className="user-profile">
            <img src={user.avatar} alt={user.name} />
            <h2>{user.name}</h2>
            <p>{user.email}</p>
        </div>
    );
};

export default UserProfile;
```

**Custom Hook Example:**
```jsx
// Custom hook for API calls
const useApi = (url) => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    
    useEffect(() => {
        fetch(url)
            .then(response => response.json())
            .then(setData)
            .catch(setError)
            .finally(() => setLoading(false));
    }, [url]);
    
    return { data, loading, error };
};
```''',
                'language': 'react',
                'difficulty': 'intermediate',
                'category': 'components',
                'tags': ['react', 'hooks', 'components', 'state'],
                'quality_score': 9.6,
                'source_type': 'react_docs'
            }
        ]
        
        # Combine all knowledge items
        all_knowledge_items = (
            python_knowledge_items + javascript_knowledge_items + 
            html_knowledge_items + css_knowledge_items + react_knowledge_items
        )
        
        # Add knowledge items to database
        for item_data in all_knowledge_items:
            knowledge_item = KnowledgeBase(**item_data)
            db.session.add(knowledge_item)
        
        # Create Project Templates
        project_templates = [
            {
                'name': 'Flask Web Application',
                'description': 'Complete Flask web app with authentication, database, and admin panel',
                'language': 'python',
                'category': 'web-app',
                'template_code': '''from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        user = User(username=username, email=email,
                   password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful!')
        return redirect(url_for('index'))
    
    return render_template('register.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)''',
                'file_structure': {
                    'app.py': 'Main application file',
                    'templates/': 'HTML templates directory',
                    'static/': 'CSS, JS, images directory',
                    'requirements.txt': 'Python dependencies'
                },
                'dependencies': ['Flask', 'Flask-SQLAlchemy', 'Werkzeug'],
                'instructions': '''1. Install dependencies: pip install flask flask-sqlalchemy
2. Run: python app.py
3. Visit http://localhost:5000
4. Customize templates in templates/ directory''',
                'difficulty': 'intermediate',
                'popularity_score': 8.5,
                'is_featured': True
            },
            {
                'name': 'React Todo App with Hooks',
                'description': 'Modern React todo application using functional components and hooks',
                'language': 'react',
                'category': 'web-app',
                'template_code': '''import React, { useState, useEffect } from 'react';
import './App.css';

const TodoApp = () => {
    const [todos, setTodos] = useState([]);
    const [inputValue, setInputValue] = useState('');
    
    // Load todos from localStorage
    useEffect(() => {
        const savedTodos = localStorage.getItem('todos');
        if (savedTodos) {
            setTodos(JSON.parse(savedTodos));
        }
    }, []);
    
    // Save todos to localStorage
    useEffect(() => {
        localStorage.setItem('todos', JSON.stringify(todos));
    }, [todos]);
    
    const addTodo = () => {
        if (inputValue.trim()) {
            setTodos([...todos, {
                id: Date.now(),
                text: inputValue,
                completed: false
            }]);
            setInputValue('');
        }
    };
    
    const toggleTodo = (id) => {
        setTodos(todos.map(todo =>
            todo.id === id ? { ...todo, completed: !todo.completed } : todo
        ));
    };
    
    const deleteTodo = (id) => {
        setTodos(todos.filter(todo => todo.id !== id));
    };
    
    return (
        <div className="todo-app">
            <h1>Todo List</h1>
            <div className="input-section">
                <input
                    type="text"
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && addTodo()}
                    placeholder="Add a new todo..."
                />
                <button onClick={addTodo}>Add</button>
            </div>
            <ul className="todo-list">
                {todos.map(todo => (
                    <li key={todo.id} className={todo.completed ? 'completed' : ''}>
                        <span onClick={() => toggleTodo(todo.id)}>
                            {todo.text}
                        </span>
                        <button onClick={() => deleteTodo(todo.id)}>Delete</button>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default TodoApp;''',
                'file_structure': {
                    'src/App.js': 'Main React component',
                    'src/App.css': 'Styling',
                    'public/index.html': 'HTML template',
                    'package.json': 'Dependencies and scripts'
                },
                'dependencies': ['react', 'react-dom'],
                'instructions': '''1. Create React app: npx create-react-app todo-app
2. Replace App.js with this code
3. Run: npm start
4. Visit http://localhost:3000''',
                'difficulty': 'beginner',
                'popularity_score': 9.2,
                'is_featured': True
            }
        ]
        
        for template_data in project_templates:
            template = ProjectTemplate(**template_data)
            db.session.add(template)
        
        # Create Code Examples
        code_examples = [
            {
                'title': 'Python List Comprehension',
                'description': 'Concise way to create lists with conditions',
                'language': 'python',
                'category': 'algorithms',
                'code_snippet': '''# Basic list comprehension
squares = [x**2 for x in range(10)]

# With condition
even_squares = [x**2 for x in range(10) if x % 2 == 0]

# Nested loops
matrix = [[i*j for j in range(3)] for i in range(3)]

# String processing
words = ['hello', 'world', 'python']
capitalized = [word.upper() for word in words if len(word) > 4]''',
                'explanation': 'List comprehensions provide a concise way to create lists. They can include conditions and nested loops.',
                'input_example': 'range(10)',
                'output_example': '[0, 1, 4, 9, 16, 25, 36, 49, 64, 81]',
                'related_concepts': ['loops', 'conditionals', 'lists'],
                'difficulty': 'intermediate',
                'is_tested': True
            },
            {
                'title': 'JavaScript Array Methods',
                'description': 'Modern array manipulation methods',
                'language': 'javascript',
                'category': 'data-structures',
                'code_snippet': '''const numbers = [1, 2, 3, 4, 5];

// Map - transform each element
const doubled = numbers.map(n => n * 2);

// Filter - select elements
const evens = numbers.filter(n => n % 2 === 0);

// Reduce - accumulate values
const sum = numbers.reduce((acc, n) => acc + n, 0);

// Find - locate element
const found = numbers.find(n => n > 3);

// Some/Every - test conditions
const hasEven = numbers.some(n => n % 2 === 0);
const allPositive = numbers.every(n => n > 0);''',
                'explanation': 'JavaScript array methods provide functional programming approaches to data manipulation.',
                'input_example': '[1, 2, 3, 4, 5]',
                'output_example': 'doubled: [2, 4, 6, 8, 10], sum: 15',
                'related_concepts': ['arrays', 'functional-programming', 'methods'],
                'difficulty': 'intermediate',
                'is_tested': True
            }
        ]
        
        for example_data in code_examples:
            example = CodeExample(**example_data)
            db.session.add(example)
        
        # Create Learning Paths
        learning_paths = [
            {
                'name': 'Python Fundamentals to Web Development',
                'description': 'Complete path from Python basics to building web applications',
                'language': 'python',
                'target_audience': 'beginner',
                'estimated_duration': '6 weeks',
                'curriculum': [
                    {'week': 1, 'topic': 'Python Syntax and Variables', 'concepts': ['variables', 'data types', 'operators']},
                    {'week': 2, 'topic': 'Control Structures', 'concepts': ['if statements', 'loops', 'functions']},
                    {'week': 3, 'topic': 'Data Structures', 'concepts': ['lists', 'dictionaries', 'sets']},
                    {'week': 4, 'topic': 'Object-Oriented Programming', 'concepts': ['classes', 'inheritance', 'polymorphism']},
                    {'week': 5, 'topic': 'File I/O and Error Handling', 'concepts': ['file operations', 'exceptions', 'debugging']},
                    {'week': 6, 'topic': 'Web Development with Flask', 'concepts': ['routing', 'templates', 'databases']}
                ],
                'prerequisites': ['Basic computer skills', 'Text editor familiarity'],
                'learning_objectives': [
                    'Write Python programs using proper syntax',
                    'Build web applications with Flask',
                    'Handle data and databases',
                    'Debug and test code effectively'
                ],
                'completion_criteria': [
                    'Complete all weekly assignments',
                    'Build a final web project',
                    'Pass knowledge assessments'
                ],
                'is_active': True
            },
            {
                'name': 'JavaScript to React Mastery',
                'description': 'Master JavaScript fundamentals and React development',
                'language': 'javascript',
                'target_audience': 'intermediate',
                'estimated_duration': '8 weeks',
                'curriculum': [
                    {'week': 1, 'topic': 'JavaScript ES6+ Features', 'concepts': ['arrow functions', 'destructuring', 'modules']},
                    {'week': 2, 'topic': 'Async Programming', 'concepts': ['promises', 'async/await', 'fetch API']},
                    {'week': 3, 'topic': 'DOM Manipulation', 'concepts': ['selectors', 'events', 'dynamic content']},
                    {'week': 4, 'topic': 'React Fundamentals', 'concepts': ['components', 'props', 'state']},
                    {'week': 5, 'topic': 'React Hooks', 'concepts': ['useState', 'useEffect', 'custom hooks']},
                    {'week': 6, 'topic': 'State Management', 'concepts': ['context API', 'useReducer', 'state patterns']},
                    {'week': 7, 'topic': 'React Router', 'concepts': ['routing', 'navigation', 'protected routes']},
                    {'week': 8, 'topic': 'Testing and Deployment', 'concepts': ['unit tests', 'integration tests', 'deployment']}
                ],
                'prerequisites': ['HTML/CSS knowledge', 'Basic programming concepts'],
                'learning_objectives': [
                    'Master modern JavaScript features',
                    'Build React applications',
                    'Implement state management',
                    'Deploy production applications'
                ],
                'completion_criteria': [
                    'Build 3 React projects',
                    'Write comprehensive tests',
                    'Deploy to production'
                ],
                'is_active': True
            }
        ]
        
        for path_data in learning_paths:
            path = LearningPath(**path_data)
            db.session.add(path)
        
        # Create System Configuration
        system_configs = [
            {
                'config_key': 'supported_languages',
                'config_value': ['python', 'javascript', 'html', 'css', 'react'],
                'description': 'List of programming languages supported by the system',
                'category': 'system_settings'
            },
            {
                'config_key': 'ai_response_settings',
                'config_value': {
                    'max_response_length': 2000,
                    'include_code_examples': True,
                    'personality_tone': 'helpful_expert',
                    'include_related_topics': True
                },
                'description': 'Configuration for AI response generation',
                'category': 'ai_settings'
            },
            {
                'config_key': 'quality_thresholds',
                'config_value': {
                    'minimum_content_length': 100,
                    'minimum_quality_score': 7.0,
                    'require_code_examples': True
                },
                'description': 'Quality requirements for knowledge base content',
                'category': 'data_quality'
            }
        ]
        
        for config_data in system_configs:
            config = SystemConfig(**config_data)
            db.session.add(config)
        
        # Commit all changes
        db.session.commit()
        
        print("✅ Database initialization complete!")
        print(f"📚 Added {len(all_knowledge_items)} knowledge base items")
        print(f"🏗️ Added {len(project_templates)} project templates")
        print(f"💡 Added {len(code_examples)} code examples")
        print(f"🛤️ Added {len(learning_paths)} learning paths")
        print(f"⚙️ Added {len(system_configs)} system configurations")
        print("\n🌟 PyLearnAI is ready for multi-language learning!")


if __name__ == '__main__':
    initialize_multi_language_database()