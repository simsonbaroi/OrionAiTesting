"""
Web Framework Expert System
Specialized AI for HTML, CSS, JavaScript, React, and modern web frameworks
"""

import json
import sqlite3
import re
from typing import Dict, List, Optional
from datetime import datetime

class WebFrameworkExpert:
    """
    Expert system for web development frameworks and technologies
    """
    
    def __init__(self, db_path: str = "instance/web_expert.db"):
        self.db_path = db_path
        self.initialize_web_database()
        self.load_framework_knowledge()
    
    def initialize_web_database(self):
        """Initialize web development knowledge database"""
        import os
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Framework patterns and best practices
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS framework_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    framework TEXT NOT NULL,
                    pattern_name TEXT NOT NULL,
                    pattern_code TEXT NOT NULL,
                    description TEXT,
                    complexity_level TEXT DEFAULT 'intermediate',
                    usage_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Component library
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS component_library (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    component_name TEXT NOT NULL,
                    framework TEXT NOT NULL,
                    component_code TEXT NOT NULL,
                    props_schema TEXT,
                    usage_example TEXT,
                    category TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Performance optimizations
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_tips (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    framework TEXT NOT NULL,
                    optimization_type TEXT NOT NULL,
                    technique TEXT NOT NULL,
                    code_example TEXT,
                    performance_impact TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    def load_framework_knowledge(self):
        """Load comprehensive framework knowledge"""
        self.framework_knowledge = {
            'react': {
                'hooks': {
                    'useState': {
                        'pattern': "const [state, setState] = useState(initialValue)",
                        'best_practices': [
                            "Use functional updates for state based on previous state",
                            "Initialize state with the correct type",
                            "Avoid mutating state directly"
                        ]
                    },
                    'useEffect': {
                        'pattern': "useEffect(() => { /* effect */ return cleanup }, [dependencies])",
                        'best_practices': [
                            "Always specify dependencies array",
                            "Return cleanup function for subscriptions",
                            "Use multiple useEffect for different concerns"
                        ]
                    },
                    'useCallback': {
                        'pattern': "const memoizedCallback = useCallback(() => { /* callback */ }, [deps])",
                        'best_practices': [
                            "Use for functions passed to child components",
                            "Include all used variables in dependencies",
                            "Don't overuse - profile performance first"
                        ]
                    },
                    'useMemo': {
                        'pattern': "const memoizedValue = useMemo(() => computeExpensiveValue(a, b), [a, b])",
                        'best_practices': [
                            "Use for expensive calculations only",
                            "Include all dependencies",
                            "Profile before optimizing"
                        ]
                    }
                },
                'patterns': {
                    'component_composition': {
                        'code': '''
// Composition over inheritance
const Layout = ({ children, sidebar }) => (
  <div className="layout">
    <aside>{sidebar}</aside>
    <main>{children}</main>
  </div>
);

const App = () => (
  <Layout sidebar={<Navigation />}>
    <Content />
  </Layout>
);
                        ''',
                        'description': "Use composition to build flexible components"
                    },
                    'custom_hooks': {
                        'code': '''
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
                        ''',
                        'description': "Extract stateful logic into reusable hooks"
                    }
                }
            },
            'javascript': {
                'modern_features': {
                    'async_await': {
                        'pattern': "async function fetchData() { try { const data = await fetch(url); return data.json(); } catch (error) { console.error(error); } }",
                        'best_practices': [
                            "Always use try-catch with async/await",
                            "Handle both success and error cases",
                            "Use Promise.all for parallel operations"
                        ]
                    },
                    'destructuring': {
                        'pattern': "const { name, age, ...rest } = user; const [first, second, ...others] = array;",
                        'best_practices': [
                            "Use default values when destructuring",
                            "Rename variables for clarity",
                            "Use rest operator for remaining properties"
                        ]
                    },
                    'modules': {
                        'pattern': "export const utils = { helper1, helper2 }; import { utils } from './utils';",
                        'best_practices': [
                            "Use named exports for utilities",
                            "Use default exports for main functionality",
                            "Organize imports logically"
                        ]
                    }
                },
                'performance': {
                    'debouncing': {
                        'code': '''
const debounce = (func, delay) => {
  let timeoutId;
  return (...args) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func.apply(this, args), delay);
  };
};

// Usage
const debouncedSearch = debounce(searchFunction, 300);
                        ''',
                        'description': "Debounce function calls to improve performance"
                    },
                    'memoization': {
                        'code': '''
const memoize = (fn) => {
  const cache = new Map();
  return (...args) => {
    const key = JSON.stringify(args);
    if (cache.has(key)) return cache.get(key);
    const result = fn(...args);
    cache.set(key, result);
    return result;
  };
};
                        ''',
                        'description': "Cache function results to avoid recomputation"
                    }
                }
            },
            'css': {
                'modern_layouts': {
                    'grid': {
                        'pattern': "display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem;",
                        'best_practices': [
                            "Use auto-fit for responsive layouts",
                            "Define grid areas for complex layouts",
                            "Use gap instead of margins"
                        ]
                    },
                    'flexbox': {
                        'pattern': "display: flex; justify-content: space-between; align-items: center; gap: 1rem;",
                        'best_practices': [
                            "Use gap for spacing between items",
                            "Understand main and cross axes",
                            "Use flex-wrap for responsive designs"
                        ]
                    }
                },
                'responsive_design': {
                    'mobile_first': {
                        'code': '''
/* Mobile-first approach */
.container {
  padding: 1rem;
  width: 100%;
}

@media (min-width: 768px) {
  .container {
    padding: 2rem;
    max-width: 1200px;
    margin: 0 auto;
  }
}
                        ''',
                        'description': "Start with mobile styles, then enhance for larger screens"
                    },
                    'container_queries': {
                        'code': '''
.card {
  container-type: inline-size;
}

@container (min-width: 300px) {
  .card-content {
    display: flex;
    gap: 1rem;
  }
}
                        ''',
                        'description': "Use container queries for component-level responsiveness"
                    }
                }
            },
            'html': {
                'semantic_elements': {
                    'structure': {
                        'code': '''
<main>
  <header>
    <nav aria-label="Main navigation">
      <ul>
        <li><a href="#home">Home</a></li>
        <li><a href="#about">About</a></li>
      </ul>
    </nav>
  </header>
  
  <section aria-labelledby="features-heading">
    <h2 id="features-heading">Features</h2>
    <article>
      <h3>Feature 1</h3>
      <p>Description</p>
    </article>
  </section>
  
  <aside>
    <h2>Related Links</h2>
  </aside>
  
  <footer>
    <p>&copy; 2025 Company Name</p>
  </footer>
</main>
                        ''',
                        'description': "Use semantic HTML for better accessibility and SEO"
                    }
                },
                'accessibility': {
                    'aria_labels': {
                        'code': '''
<button aria-label="Close dialog" onclick="closeDialog()">
  <svg aria-hidden="true"><!-- close icon --></svg>
</button>

<input type="search" aria-describedby="search-help" />
<div id="search-help">Enter keywords to search</div>

<img src="chart.png" alt="Sales increased 25% from January to March" />
                        ''',
                        'description': "Use ARIA labels and descriptions for better accessibility"
                    }
                }
            }
        }
    
    def get_framework_suggestions(self, framework: str, context: str = "") -> List[Dict]:
        """Get framework-specific suggestions and patterns"""
        suggestions = []
        
        if framework.lower() in self.framework_knowledge:
            fw_knowledge = self.framework_knowledge[framework.lower()]
            
            for category, items in fw_knowledge.items():
                for item_name, item_data in items.items():
                    suggestion = {
                        'category': category,
                        'name': item_name,
                        'pattern': item_data.get('pattern', ''),
                        'code': item_data.get('code', ''),
                        'description': item_data.get('description', ''),
                        'best_practices': item_data.get('best_practices', [])
                    }
                    suggestions.append(suggestion)
        
        return suggestions
    
    def analyze_web_code(self, code: str, file_type: str) -> Dict:
        """Analyze web code for improvements and issues"""
        analysis = {
            'file_type': file_type,
            'issues': [],
            'suggestions': [],
            'best_practices': [],
            'performance_tips': []
        }
        
        if file_type == 'react' or 'jsx' in file_type:
            analysis.update(self._analyze_react_code(code))
        elif file_type == 'javascript' or file_type == 'js':
            analysis.update(self._analyze_javascript_code(code))
        elif file_type == 'css':
            analysis.update(self._analyze_css_code(code))
        elif file_type == 'html':
            analysis.update(self._analyze_html_code(code))
        
        return analysis
    
    def _analyze_react_code(self, code: str) -> Dict:
        """Analyze React code for patterns and improvements"""
        analysis = {'issues': [], 'suggestions': [], 'best_practices': [], 'performance_tips': []}
        
        # Check for React best practices
        if 'useState' in code and 'useEffect' in code:
            analysis['best_practices'].append("Good use of React hooks")
        
        if re.search(r'function\s+\w+\s*\([^)]*\)\s*{', code):
            analysis['suggestions'].append("Consider using arrow functions for components")
        
        if 'key=' not in code and '.map(' in code:
            analysis['issues'].append("Missing 'key' prop in list rendering")
        
        if re.search(r'useEffect\([^,]+\)(?!\s*,)', code):
            analysis['issues'].append("useEffect missing dependency array")
        
        # Performance checks
        if 'React.memo' not in code and 'memo' not in code:
            analysis['performance_tips'].append("Consider using React.memo for performance optimization")
        
        return analysis
    
    def _analyze_javascript_code(self, code: str) -> Dict:
        """Analyze JavaScript code for improvements"""
        analysis = {'issues': [], 'suggestions': [], 'best_practices': [], 'performance_tips': []}
        
        # Check for modern JavaScript usage
        if 'var ' in code:
            analysis['suggestions'].append("Use 'let' or 'const' instead of 'var'")
        
        if '==' in code and '===' not in code:
            analysis['suggestions'].append("Use strict equality (===) instead of loose equality (==)")
        
        if '.innerHTML' in code:
            analysis['issues'].append("Using innerHTML can be a security risk - consider textContent or DOM methods")
        
        # Async/await checks
        if 'Promise' in code and 'async' not in code:
            analysis['suggestions'].append("Consider using async/await for better readability")
        
        return analysis
    
    def _analyze_css_code(self, code: str) -> Dict:
        """Analyze CSS code for improvements"""
        analysis = {'issues': [], 'suggestions': [], 'best_practices': [], 'performance_tips': []}
        
        # Modern CSS checks
        if 'float:' in code:
            analysis['suggestions'].append("Consider using Flexbox or Grid instead of float")
        
        if '@media' not in code and ('width' in code or 'height' in code):
            analysis['suggestions'].append("Consider adding responsive design with media queries")
        
        # Performance checks
        if '*' in code:
            analysis['performance_tips'].append("Avoid universal selector (*) for better performance")
        
        if re.search(r'#\w+\s+\w+', code):
            analysis['performance_tips'].append("Avoid over-qualifying selectors")
        
        return analysis
    
    def _analyze_html_code(self, code: str) -> Dict:
        """Analyze HTML code for accessibility and semantics"""
        analysis = {'issues': [], 'suggestions': [], 'best_practices': [], 'accessibility_tips': []}
        
        # Accessibility checks
        if '<img' in code and 'alt=' not in code:
            analysis['issues'].append("Images missing alt attributes")
        
        if '<button' in code and 'aria-label=' not in code and '>' in code:
            button_content = re.search(r'<button[^>]*>([^<]*)<', code)
            if button_content and not button_content.group(1).strip():
                analysis['accessibility_tips'].append("Buttons need accessible labels")
        
        # Semantic HTML checks
        if '<div' in code and not any(tag in code for tag in ['<main', '<section', '<article', '<header', '<footer']):
            analysis['suggestions'].append("Consider using semantic HTML elements")
        
        return analysis
    
    def generate_component(self, component_type: str, framework: str, props: Dict = None) -> str:
        """Generate component code based on type and framework"""
        if framework.lower() == 'react':
            return self._generate_react_component(component_type, props or {})
        elif framework.lower() == 'vue':
            return self._generate_vue_component(component_type, props or {})
        else:
            return self._generate_vanilla_component(component_type, props or {})
    
    def _generate_react_component(self, component_type: str, props: Dict) -> str:
        """Generate React component"""
        components = {
            'button': '''
import React from 'react';

interface ButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: 'primary' | 'secondary' | 'danger';
  disabled?: boolean;
}

const Button: React.FC<ButtonProps> = ({ 
  children, 
  onClick, 
  variant = 'primary', 
  disabled = false 
}) => {
  return (
    <button
      className={`btn btn-${variant}`}
      onClick={onClick}
      disabled={disabled}
      type="button"
    >
      {children}
    </button>
  );
};

export default Button;
            ''',
            'modal': '''
import React, { useEffect } from 'react';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
}

const Modal: React.FC<ModalProps> = ({ isOpen, onClose, title, children }) => {
  useEffect(() => {
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onClose();
    };
    
    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }
    
    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);
  
  if (!isOpen) return null;
  
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <header className="modal-header">
          <h2>{title}</h2>
          <button onClick={onClose} aria-label="Close modal">×</button>
        </header>
        <div className="modal-body">
          {children}
        </div>
      </div>
    </div>
  );
};

export default Modal;
            '''
        }
        
        return components.get(component_type.lower(), f"// {component_type} component template")
    
    def _generate_vue_component(self, component_type: str, props: Dict) -> str:
        """Generate Vue component"""
        return f"""
<template>
  <div class="{component_type.lower()}">
    <!-- {component_type} component -->
  </div>
</template>

<script>
export default {{
  name: '{component_type}',
  props: {json.dumps(props, indent=2) if props else '{}'}
}}
</script>

<style scoped>
.{component_type.lower()} {{
  /* Component styles */
}}
</style>
        """
    
    def _generate_vanilla_component(self, component_type: str, props: Dict) -> str:
        """Generate vanilla JavaScript component"""
        return f"""
class {component_type} {{
  constructor(element, options = {{}}) {{
    this.element = element;
    this.options = {{ ...this.defaults, ...options }};
    this.init();
  }}
  
  get defaults() {{
    return {json.dumps(props, indent=4) if props else '{}'};
  }}
  
  init() {{
    this.render();
    this.bindEvents();
  }}
  
  render() {{
    // Render component
  }}
  
  bindEvents() {{
    // Bind event listeners
  }}
}}
        """
    
    def get_performance_tips(self, framework: str) -> List[Dict]:
        """Get performance optimization tips for specific framework"""
        tips = {
            'react': [
                {
                    'tip': 'Use React.memo for pure components',
                    'code': 'const MyComponent = React.memo(({ prop }) => <div>{prop}</div>);',
                    'impact': 'Prevents unnecessary re-renders'
                },
                {
                    'tip': 'Implement code splitting with lazy loading',
                    'code': 'const LazyComponent = React.lazy(() => import("./Component"));',
                    'impact': 'Reduces initial bundle size'
                },
                {
                    'tip': 'Use useCallback for stable function references',
                    'code': 'const handleClick = useCallback(() => {}, []);',
                    'impact': 'Prevents child component re-renders'
                }
            ],
            'javascript': [
                {
                    'tip': 'Use requestAnimationFrame for animations',
                    'code': 'requestAnimationFrame(() => { /* animation code */ });',
                    'impact': 'Smooth 60fps animations'
                },
                {
                    'tip': 'Implement virtual scrolling for large lists',
                    'code': '// Only render visible items in viewport',
                    'impact': 'Handle thousands of list items efficiently'
                }
            ],
            'css': [
                {
                    'tip': 'Use transform and opacity for animations',
                    'code': 'transform: translateX(100px); opacity: 0.5;',
                    'impact': 'Hardware-accelerated animations'
                },
                {
                    'tip': 'Minimize layout thrashing',
                    'code': 'will-change: transform; /* for elements that will animate */',
                    'impact': 'Prevents unnecessary layout recalculations'
                }
            ]
        }
        
        return tips.get(framework.lower(), [])

# Initialize web framework expert
web_expert = WebFrameworkExpert()