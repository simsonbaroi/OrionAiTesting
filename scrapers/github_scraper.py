import requests
import logging
import time
import base64
from typing import List, Dict, Optional
from config import Config
from scrapers.web_scraper import WebScraper

logger = logging.getLogger(__name__)

class GitHubScraper(WebScraper):
    def __init__(self):
        super().__init__()
        self.api_token = Config.GITHUB_API_TOKEN
        self.base_api_url = "https://api.github.com"
        self.repos = Config.GITHUB_PYTHON_REPOS
        self.session.headers.update({
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'PyLearnAI/1.0'
        })
        
        if self.api_token:
            self.session.headers['Authorization'] = f'token {self.api_token}'
    
    def scrape_github_repositories(self, max_files_per_repo: int = 20) -> List[Dict]:
        """
        Scrape Python files from specified GitHub repositories
        """
        logger.info("Starting GitHub repository scraping")
        all_results = []
        
        for repo in self.repos:
            logger.info(f"Scraping repository: {repo}")
            
            try:
                # Get repository information
                repo_info = self.get_repository_info(repo)
                if not repo_info:
                    continue
                
                # Get Python files from repository
                python_files = self.get_python_files(repo, max_files_per_repo)
                
                # Process each file
                for file_info in python_files:
                    file_content = self.get_file_content(repo, file_info['path'])
                    if file_content:
                        processed_item = self.process_github_file(
                            repo, file_info, file_content, repo_info
                        )
                        if processed_item:
                            all_results.append(processed_item)
                
                # Rate limiting for GitHub API
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error scraping repository {repo}: {str(e)}")
                continue
        
        logger.info(f"GitHub scraping completed. Total items: {len(all_results)}")
        return all_results
    
    def get_repository_info(self, repo: str) -> Optional[Dict]:
        """
        Get repository information from GitHub API
        """
        try:
            response = self.session.get(f"{self.base_api_url}/repos/{repo}", timeout=self.timeout)
            
            if response.status_code == 404:
                logger.warning(f"Repository not found: {repo}")
                return None
            elif response.status_code == 403:
                logger.warning(f"Rate limited or access denied for repository: {repo}")
                return None
            
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Error getting repository info for {repo}: {str(e)}")
            return None
    
    def get_python_files(self, repo: str, max_files: int = 20) -> List[Dict]:
        """
        Get Python files from a repository
        """
        try:
            # Search for Python files in the repository
            query = f"repo:{repo} extension:py"
            params = {
                'q': query,
                'sort': 'indexed',  # Get recently indexed files
                'per_page': min(max_files, 100)  # API limit
            }
            
            response = self.session.get(
                f"{self.base_api_url}/search/code",
                params=params,
                timeout=self.timeout
            )
            
            if response.status_code == 403:
                logger.warning(f"Rate limited for repository: {repo}")
                return []
            
            response.raise_for_status()
            data = response.json()
            
            files = []
            for item in data.get('items', []):
                # Filter out test files and very large files
                if self._is_relevant_python_file(item):
                    files.append({
                        'path': item['path'],
                        'name': item['name'],
                        'size': item.get('size', 0),
                        'sha': item['sha']
                    })
            
            logger.info(f"Found {len(files)} Python files in {repo}")
            return files[:max_files]
            
        except requests.RequestException as e:
            logger.error(f"Error getting Python files for {repo}: {str(e)}")
            return []
    
    def get_file_content(self, repo: str, file_path: str) -> Optional[str]:
        """
        Get content of a specific file from GitHub
        """
        try:
            response = self.session.get(
                f"{self.base_api_url}/repos/{repo}/contents/{file_path}",
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                logger.warning(f"Failed to get file content: {repo}/{file_path}")
                return None
            
            data = response.json()
            
            # Decode base64 content
            if data.get('encoding') == 'base64':
                content = base64.b64decode(data['content']).decode('utf-8')
                return content
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting file content for {repo}/{file_path}: {str(e)}")
            return None
    
    def _is_relevant_python_file(self, file_item: Dict) -> bool:
        """
        Check if a Python file is relevant for learning
        """
        path = file_item.get('path', '').lower()
        name = file_item.get('name', '').lower()
        size = file_item.get('size', 0)
        
        # Skip test files
        if any(test_indicator in path for test_indicator in ['test_', 'tests/', '/test/', '_test.py']):
            return False
        
        # Skip very large files (> 50KB)
        if size > 50000:
            return False
        
        # Skip very small files (< 100 bytes)
        if size < 100:
            return False
        
        # Skip certain file types
        skip_patterns = [
            '__pycache__',
            '.pyc',
            'setup.py',
            'conftest.py',
            'migrate',
            'migration'
        ]
        
        for pattern in skip_patterns:
            if pattern in path:
                return False
        
        # Prefer certain file types
        prefer_patterns = [
            'example',
            'tutorial',
            'demo',
            '/src/',
            '/lib/',
            'util',
            'helper'
        ]
        
        for pattern in prefer_patterns:
            if pattern in path:
                return True
        
        return True  # Default to include
    
    def process_github_file(self, repo: str, file_info: Dict, content: str, repo_info: Dict) -> Optional[Dict]:
        """
        Process GitHub file content into structured format
        """
        try:
            if not content or len(content) < 50:
                return None
            
            # Extract useful information from the code
            analysis = self.analyze_python_code(content)
            
            if not analysis['has_meaningful_content']:
                return None
            
            # Create title from file path
            title = self._create_title_from_path(file_info['path'])
            
            # Create documentation from code
            documentation = self._create_documentation_from_code(content, analysis)
            
            # Calculate quality score
            quality_score = self._calculate_github_quality(content, analysis, repo_info)
            
            if quality_score < Config.MIN_QUALITY_SCORE:
                return None
            
            return {
                'title': title,
                'content': documentation,
                'source_url': f"https://github.com/{repo}/blob/main/{file_info['path']}",
                'source_type': 'github',
                'repository': repo,
                'file_path': file_info['path'],
                'file_size': file_info.get('size', 0),
                'code_analysis': analysis,
                'quality_score': quality_score,
                'scraped_at': time.time()
            }
            
        except Exception as e:
            logger.error(f"Error processing GitHub file {repo}/{file_info['path']}: {str(e)}")
            return None
    
    def analyze_python_code(self, code: str) -> Dict:
        """
        Analyze Python code to extract meaningful information
        """
        analysis = {
            'has_meaningful_content': False,
            'functions': [],
            'classes': [],
            'imports': [],
            'docstrings': [],
            'complexity_score': 0.0
        }
        
        try:
            import ast
            
            # Parse the code
            tree = ast.parse(code)
            
            # Extract functions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_info = {
                        'name': node.name,
                        'args': [arg.arg for arg in node.args.args],
                        'docstring': ast.get_docstring(node) or ''
                    }
                    analysis['functions'].append(func_info)
                
                elif isinstance(node, ast.ClassDef):
                    class_info = {
                        'name': node.name,
                        'docstring': ast.get_docstring(node) or '',
                        'methods': []
                    }
                    
                    # Get methods
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            class_info['methods'].append(item.name)
                    
                    analysis['classes'].append(class_info)
                
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        analysis['imports'].append(alias.name)
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        for alias in node.names:
                            analysis['imports'].append(f"{node.module}.{alias.name}")
            
            # Extract docstrings
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
                    docstring = ast.get_docstring(node)
                    if docstring and len(docstring) > 20:
                        analysis['docstrings'].append(docstring)
            
            # Calculate complexity score
            analysis['complexity_score'] = len(analysis['functions']) * 0.1 + len(analysis['classes']) * 0.2
            
            # Determine if content is meaningful
            if (len(analysis['functions']) > 0 or len(analysis['classes']) > 0 or 
                len(analysis['docstrings']) > 0):
                analysis['has_meaningful_content'] = True
            
        except SyntaxError:
            logger.warning("Syntax error in Python code, skipping analysis")
        except Exception as e:
            logger.error(f"Error analyzing Python code: {str(e)}")
        
        return analysis
    
    def _create_title_from_path(self, file_path: str) -> str:
        """
        Create a meaningful title from file path
        """
        # Get filename without extension
        filename = file_path.split('/')[-1].replace('.py', '')
        
        # Convert underscores and hyphens to spaces
        title = filename.replace('_', ' ').replace('-', ' ')
        
        # Add directory context if meaningful
        path_parts = file_path.split('/')[:-1]  # Exclude filename
        if path_parts:
            # Get the most relevant directory
            relevant_dirs = [part for part in path_parts if part not in ['src', 'lib', 'python']]
            if relevant_dirs:
                context = relevant_dirs[-1]  # Use the most specific directory
                title = f"{context.replace('_', ' ')} - {title}"
        
        return title.title()
    
    def _create_documentation_from_code(self, code: str, analysis: Dict) -> str:
        """
        Create documentation text from code analysis
        """
        doc_parts = []
        
        # Add file overview
        if analysis['classes']:
            doc_parts.append(f"This module defines {len(analysis['classes'])} class(es): {', '.join([c['name'] for c in analysis['classes']])}")
        
        if analysis['functions']:
            doc_parts.append(f"This module contains {len(analysis['functions'])} function(s): {', '.join([f['name'] for f in analysis['functions']])}")
        
        # Add imports summary
        if analysis['imports']:
            important_imports = [imp for imp in analysis['imports'] if not imp.startswith('_')][:5]
            if important_imports:
                doc_parts.append(f"Key imports: {', '.join(important_imports)}")
        
        # Add docstrings
        if analysis['docstrings']:
            doc_parts.append("\nDocumentation:")
            for docstring in analysis['docstrings'][:3]:  # Limit to first 3 docstrings
                doc_parts.append(f"- {docstring.strip()}")
        
        # Add code examples (functions and classes)
        if analysis['functions'] or analysis['classes']:
            doc_parts.append("\nCode examples:")
            
            # Add function examples
            for func in analysis['functions'][:2]:  # Limit to first 2 functions
                args_str = ', '.join(func['args']) if func['args'] else ''
                doc_parts.append(f"```python\ndef {func['name']}({args_str}):\n    # {func['docstring'][:100] if func['docstring'] else 'Implementation details...'}\n```")
            
            # Add class examples
            for cls in analysis['classes'][:1]:  # Limit to first class
                methods_str = ', '.join(cls['methods'][:3]) if cls['methods'] else 'no methods'
                doc_parts.append(f"```python\nclass {cls['name']}:\n    # {cls['docstring'][:100] if cls['docstring'] else f'Class with {methods_str}'}\n```")
        
        return '\n'.join(doc_parts)
    
    def _calculate_github_quality(self, code: str, analysis: Dict, repo_info: Dict) -> float:
        """
        Calculate quality score for GitHub content
        """
        score = 0.0
        
        # Repository popularity (stars, forks)
        stars = repo_info.get('stargazers_count', 0)
        if stars > 1000:
            score += 0.3
        elif stars > 100:
            score += 0.2
        elif stars > 10:
            score += 0.1
        
        # Code complexity and structure
        if analysis['has_meaningful_content']:
            score += 0.2
        
        if len(analysis['functions']) > 0:
            score += 0.1
        
        if len(analysis['classes']) > 0:
            score += 0.1
        
        if len(analysis['docstrings']) > 0:
            score += 0.2
        
        # Code quality indicators
        if any(keyword in code.lower() for keyword in ['docstring', 'type hint', 'typing']):
            score += 0.1
        
        # Length check (not too short, not too long)
        code_length = len(code)
        if 200 <= code_length <= 5000:
            score += 0.1
        
        return min(score, 1.0)
