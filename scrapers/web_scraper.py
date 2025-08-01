import trafilatura
import requests
import time
import logging
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional
from config import Config

logger = logging.getLogger(__name__)

class WebScraper:
    def __init__(self, delay=None, timeout=None):
        self.delay = delay or Config.SCRAPING_DELAY
        self.timeout = timeout or Config.REQUEST_TIMEOUT
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'PyLearnAI/1.0 (Educational Python Learning Bot; Contact: github.com/user/PyLearnAI)'
        })
        self.visited_urls = set()
    
    def get_website_text_content(self, url: str) -> str:
        """
        Extract main text content from a website using trafilatura.
        Returns clean, readable text content.
        """
        try:
            logger.debug(f"Fetching content from: {url}")
            
            # Download the webpage
            downloaded = trafilatura.fetch_url(url, config=self._get_trafilatura_config())
            
            if not downloaded:
                logger.warning(f"Failed to download content from {url}")
                return ""
            
            # Extract text content
            text = trafilatura.extract(
                downloaded,
                include_links=True,
                include_tables=True,
                include_formatting=True,
                output_format='txt'
            )
            
            if not text:
                logger.warning(f"No text content extracted from {url}")
                return ""
            
            # Clean and validate content
            text = self._clean_text_content(text)
            
            if len(text) < Config.MIN_CONTENT_LENGTH:
                logger.warning(f"Content too short from {url}: {len(text)} characters")
                return ""
            
            logger.info(f"Successfully extracted {len(text)} characters from {url}")
            return text
            
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {str(e)}")
            return ""
    
    def _get_trafilatura_config(self):
        """Get trafilatura configuration for better extraction"""
        import trafilatura.settings
        config = trafilatura.settings.use_config()
        config.set("DEFAULT", "EXTRACTION_TIMEOUT", str(self.timeout))
        return config
    
    def _clean_text_content(self, text: str) -> str:
        """Clean extracted text content"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        import re
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # Remove common footer/header noise
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            # Skip very short lines that are likely navigation/noise
            if len(line) < 10:
                continue
            # Skip lines that look like navigation
            if any(nav_word in line.lower() for nav_word in ['navigation', 'menu', 'footer', 'header', 'sidebar']):
                continue
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines).strip()
    
    def scrape_multiple_urls(self, urls: List[str], max_pages: int = None) -> List[Dict]:
        """
        Scrape multiple URLs and return structured data
        """
        if max_pages is None:
            max_pages = Config.MAX_PAGES_PER_SESSION
        
        results = []
        scraped_count = 0
        
        for url in urls:
            if scraped_count >= max_pages:
                logger.info(f"Reached maximum pages limit: {max_pages}")
                break
            
            if url in self.visited_urls:
                logger.debug(f"URL already visited: {url}")
                continue
            
            try:
                # Extract content
                content = self.get_website_text_content(url)
                
                if content:
                    # Try to extract title from content
                    title = self._extract_title(content, url)
                    
                    results.append({
                        'url': url,
                        'title': title,
                        'content': content,
                        'scraped_at': time.time(),
                        'content_length': len(content)
                    })
                    
                    scraped_count += 1
                    logger.info(f"Successfully scraped {url} ({len(content)} chars)")
                else:
                    logger.warning(f"No content extracted from {url}")
                
                self.visited_urls.add(url)
                
                # Be respectful to servers
                time.sleep(self.delay)
                
            except Exception as e:
                logger.error(f"Error scraping {url}: {str(e)}")
                continue
        
        logger.info(f"Scraping completed. Processed {scraped_count} URLs, collected {len(results)} items")
        return results
    
    def _extract_title(self, content: str, url: str) -> str:
        """Extract title from content or URL"""
        # Try to find title in first few lines
        lines = content.split('\n')[:5]
        for line in lines:
            line = line.strip()
            if len(line) > 10 and len(line) < 200:
                # This might be a title
                return line
        
        # Fallback to URL-based title
        from urllib.parse import urlparse
        parsed = urlparse(url)
        path_parts = parsed.path.strip('/').split('/')
        if path_parts and path_parts[-1]:
            return path_parts[-1].replace('-', ' ').replace('_', ' ').title()
        
        return "Untitled Content"
    
    def discover_links(self, base_url: str, max_depth: int = 2) -> List[str]:
        """
        Discover related links from a base URL
        """
        discovered_urls = set()
        queue = [(base_url, 0)]
        
        while queue and len(discovered_urls) < Config.MAX_PAGES_PER_SESSION:
            url, depth = queue.pop(0)
            
            if depth > max_depth or url in self.visited_urls:
                continue
            
            try:
                response = self.session.get(url, timeout=self.timeout)
                if response.status_code != 200:
                    continue
                
                # Use trafilatura to extract links
                downloaded = response.text
                links = trafilatura.extract_links(downloaded)
                
                base_domain = urlparse(base_url).netloc
                
                for link in links:
                    absolute_url = urljoin(url, link)
                    link_domain = urlparse(absolute_url).netloc
                    
                    # Only follow links from the same domain
                    if link_domain == base_domain:
                        if absolute_url not in discovered_urls and absolute_url not in self.visited_urls:
                            discovered_urls.add(absolute_url)
                            if depth < max_depth:
                                queue.append((absolute_url, depth + 1))
                
                self.visited_urls.add(url)
                time.sleep(self.delay)
                
            except Exception as e:
                logger.error(f"Error discovering links from {url}: {str(e)}")
                continue
        
        return list(discovered_urls)
    
    def validate_content_quality(self, content: str) -> float:
        """
        Validate content quality and return a score (0.0 to 1.0)
        """
        if not content or len(content) < Config.MIN_CONTENT_LENGTH:
            return 0.0
        
        score = 0.0
        
        # Length score (optimal length around 500-5000 chars)
        length = len(content)
        if 500 <= length <= 5000:
            score += 0.3
        elif 200 <= length < 500 or 5000 < length <= 10000:
            score += 0.2
        elif 100 <= length < 200:
            score += 0.1
        
        # Python-related content
        python_keywords = ['python', 'def', 'class', 'import', 'function', 'variable', 'list', 'dict', 'tuple', 'string', 'int', 'float']
        keyword_count = sum(1 for keyword in python_keywords if keyword.lower() in content.lower())
        score += min(keyword_count * 0.05, 0.3)
        
        # Code examples
        if any(code_indicator in content for code_indicator in ['def ', 'import ', 'class ', '>>>', '```']):
            score += 0.2
        
        # Sentence structure (rough quality check)
        sentences = [s.strip() for s in content.split('.') if len(s.strip()) > 10]
        if len(sentences) >= 3:
            score += 0.2
        
        return min(score, 1.0)
