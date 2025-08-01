import logging
from typing import List, Dict
from scrapers.web_scraper import WebScraper
from config import Config
from urllib.parse import urljoin, urlparse
import re

logger = logging.getLogger(__name__)

class PythonDocsScraper(WebScraper):
    def __init__(self):
        super().__init__()
        self.base_urls = Config.PYTHON_DOCS_URLS
        
    def scrape_python_documentation(self) -> List[Dict]:
        """
        Scrape Python official documentation
        """
        logger.info("Starting Python documentation scraping")
        all_results = []
        
        for base_url in self.base_urls:
            logger.info(f"Scraping documentation from: {base_url}")
            
            try:
                # Discover related documentation pages
                urls = self.discover_documentation_links(base_url)
                
                # Scrape the discovered URLs
                results = self.scrape_multiple_urls(urls, max_pages=Config.MAX_PAGES_PER_SESSION // len(self.base_urls))
                
                # Add source type to results
                for result in results:
                    result['source_type'] = 'python_docs'
                    result['base_url'] = base_url
                    result['quality_score'] = self.validate_content_quality(result['content'])
                
                all_results.extend(results)
                logger.info(f"Collected {len(results)} pages from {base_url}")
                
            except Exception as e:
                logger.error(f"Error scraping {base_url}: {str(e)}")
                continue
        
        logger.info(f"Python documentation scraping completed. Total items: {len(all_results)}")
        return all_results
    
    def discover_documentation_links(self, base_url: str) -> List[str]:
        """
        Discover documentation links from a base URL
        """
        try:
            discovered_links = []
            
            # Start with the base URL
            discovered_links.append(base_url)
            
            # Use the generic link discovery but with documentation-specific filtering
            additional_links = self.discover_links(base_url, max_depth=2)
            
            # Filter links to keep only relevant documentation
            filtered_links = []
            for link in additional_links:
                if self._is_relevant_documentation_link(link):
                    filtered_links.append(link)
            
            discovered_links.extend(filtered_links)
            
            # Remove duplicates while preserving order
            seen = set()
            unique_links = []
            for link in discovered_links:
                if link not in seen:
                    seen.add(link)
                    unique_links.append(link)
            
            logger.info(f"Discovered {len(unique_links)} documentation links from {base_url}")
            return unique_links
            
        except Exception as e:
            logger.error(f"Error discovering documentation links from {base_url}: {str(e)}")
            return [base_url]  # Return at least the base URL
    
    def _is_relevant_documentation_link(self, url: str) -> bool:
        """
        Check if a URL is relevant Python documentation
        """
        # Must be from docs.python.org
        if 'docs.python.org' not in url:
            return False
        
        # Skip certain sections that are not useful for learning
        skip_patterns = [
            '/bugs.html',
            '/copyright.html',
            '/license.html',
            '/download.html',
            '/genindex.html',
            '/modindex.html',
            '/search.html',
            'whatsnew/changelog',
            '/c-api/',  # C API docs are too advanced
            '/extending/',  # Extension docs are specialized
            '/installing/',  # Installation docs are not code-related
        ]
        
        for pattern in skip_patterns:
            if pattern in url:
                return False
        
        # Prefer certain sections
        prefer_patterns = [
            '/tutorial/',
            '/library/',
            '/reference/',
            '/howto/',
            '/faq/',
        ]
        
        for pattern in prefer_patterns:
            if pattern in url:
                return True
        
        return True  # Default to include if not explicitly excluded
    
    def extract_code_examples(self, content: str) -> List[Dict]:
        """
        Extract code examples from documentation content
        """
        code_examples = []
        
        # Pattern for code blocks (both >>> style and regular code blocks)
        patterns = [
            r'```python\n(.*?)\n```',
            r'```\n(.*?)\n```',
            r'>>>\s*(.*?)(?=\n>>>|\n\n|\Z)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            for match in matches:
                code = match.strip()
                if len(code) > 10:  # Only meaningful code snippets
                    code_examples.append({
                        'code': code,
                        'type': 'python',
                        'context': self._extract_code_context(content, code)
                    })
        
        return code_examples
    
    def _extract_code_context(self, content: str, code: str) -> str:
        """
        Extract context around a code example
        """
        try:
            # Find the position of the code in content
            code_pos = content.find(code)
            if code_pos == -1:
                return ""
            
            # Extract surrounding text (500 chars before and after)
            start = max(0, code_pos - 500)
            end = min(len(content), code_pos + len(code) + 500)
            
            context = content[start:end]
            
            # Clean up context
            context = context.replace(code, '[CODE_EXAMPLE]')
            context = re.sub(r'\s+', ' ', context).strip()
            
            return context
            
        except Exception as e:
            logger.error(f"Error extracting code context: {str(e)}")
            return ""
    
    def categorize_documentation(self, url: str, content: str) -> str:
        """
        Categorize documentation content
        """
        url_lower = url.lower()
        content_lower = content.lower()
        
        if '/tutorial/' in url_lower:
            return 'tutorial'
        elif '/library/' in url_lower:
            return 'library_reference'
        elif '/reference/' in url_lower:
            return 'language_reference'
        elif '/howto/' in url_lower:
            return 'howto_guide'
        elif '/faq/' in url_lower:
            return 'faq'
        elif any(term in content_lower for term in ['class ', 'function', 'method']):
            return 'api_documentation'
        elif any(term in content_lower for term in ['example', 'tutorial', 'guide']):
            return 'tutorial'
        else:
            return 'general_documentation'
    
    def process_documentation_content(self, raw_results: List[Dict]) -> List[Dict]:
        """
        Process raw documentation results into structured format
        """
        processed_results = []
        
        for result in raw_results:
            try:
                content = result['content']
                url = result['url']
                
                # Extract code examples
                code_examples = self.extract_code_examples(content)
                
                # Categorize content
                category = self.categorize_documentation(url, content)
                
                # Create processed result
                processed_result = {
                    'url': url,
                    'title': result['title'],
                    'content': content,
                    'source_type': 'python_docs',
                    'category': category,
                    'code_examples': code_examples,
                    'quality_score': result.get('quality_score', 0.0),
                    'scraped_at': result['scraped_at'],
                    'content_length': len(content)
                }
                
                processed_results.append(processed_result)
                
            except Exception as e:
                logger.error(f"Error processing documentation content: {str(e)}")
                continue
        
        return processed_results
