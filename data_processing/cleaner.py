import re
import logging
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import html

logger = logging.getLogger(__name__)

class DataCleaner:
    def __init__(self):
        self.html_tags_pattern = re.compile(r'<[^>]+>')
        self.multiple_spaces_pattern = re.compile(r'\s+')
        self.multiple_newlines_pattern = re.compile(r'\n\s*\n')
        
    def clean_text_content(self, text: str) -> str:
        """
        Clean and normalize text content
        """
        if not text:
            return ""
        
        try:
            # Decode HTML entities
            text = html.unescape(text)
            
            # Remove HTML tags if present
            text = self._remove_html_tags(text)
            
            # Normalize whitespace
            text = self._normalize_whitespace(text)
            
            # Remove noise patterns
            text = self._remove_noise_patterns(text)
            
            # Clean code blocks
            text = self._clean_code_blocks(text)
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error cleaning text content: {str(e)}")
            return text
    
    def _remove_html_tags(self, text: str) -> str:
        """
        Remove HTML tags from text while preserving code blocks
        """
        try:
            # Use BeautifulSoup for better HTML parsing
            soup = BeautifulSoup(text, 'html.parser')
            
            # Convert code elements to markdown-style code blocks
            for code_elem in soup.find_all('code'):
                code_text = code_elem.get_text()
                if '\n' in code_text or len(code_text) > 50:
                    # Multi-line code block
                    code_elem.replace_with(f"\n```python\n{code_text}\n```\n")
                else:
                    # Inline code
                    code_elem.replace_with(f"`{code_text}`")
            
            # Convert pre elements to code blocks
            for pre_elem in soup.find_all('pre'):
                pre_text = pre_elem.get_text()
                pre_elem.replace_with(f"\n```\n{pre_text}\n```\n")
            
            # Get text content
            text = soup.get_text()
            
            return text
            
        except Exception as e:
            logger.warning(f"Error parsing HTML with BeautifulSoup: {str(e)}")
            # Fallback to regex
            return self.html_tags_pattern.sub('', text)
    
    def _normalize_whitespace(self, text: str) -> str:
        """
        Normalize whitespace in text
        """
        # Replace multiple spaces with single space
        text = self.multiple_spaces_pattern.sub(' ', text)
        
        # Replace multiple newlines with double newline
        text = self.multiple_newlines_pattern.sub('\n\n', text)
        
        # Remove trailing spaces from lines
        lines = text.split('\n')
        cleaned_lines = [line.rstrip() for line in lines]
        
        return '\n'.join(cleaned_lines)
    
    def _remove_noise_patterns(self, text: str) -> str:
        """
        Remove common noise patterns from text
        """
        # Common noise patterns
        noise_patterns = [
            r'^\s*Navigation\s*$',
            r'^\s*Menu\s*$',
            r'^\s*Header\s*$',
            r'^\s*Footer\s*$',
            r'^\s*Sidebar\s*$',
            r'^\s*Advertisement\s*$',
            r'^\s*Skip to content\s*$',
            r'^\s*Table of contents\s*$',
            r'^\s*Related articles\s*$',
            r'^\s*Share this\s*$',
            r'^\s*Print\s*$',
            r'^\s*Copyright.*?\d{4}.*$',
            r'^\s*Terms of use\s*$',
            r'^\s*Privacy policy\s*$',
        ]
        
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            is_noise = False
            for pattern in noise_patterns:
                if re.match(pattern, line, re.IGNORECASE):
                    is_noise = True
                    break
            
            if not is_noise and len(line.strip()) > 0:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _clean_code_blocks(self, text: str) -> str:
        """
        Clean and format code blocks
        """
        # Find and clean code blocks
        code_block_pattern = r'```(?:python)?\n?(.*?)\n?```'
        
        def clean_code_block(match):
            code = match.group(1)
            # Remove excessive indentation
            lines = code.split('\n')
            if lines:
                # Find minimum indentation (excluding empty lines)
                min_indent = float('inf')
                for line in lines:
                    if line.strip():
                        indent = len(line) - len(line.lstrip())
                        min_indent = min(min_indent, indent)
                
                if min_indent != float('inf') and min_indent > 0:
                    # Remove common indentation
                    cleaned_lines = []
                    for line in lines:
                        if line.strip():
                            cleaned_lines.append(line[min_indent:])
                        else:
                            cleaned_lines.append(line)
                    code = '\n'.join(cleaned_lines)
            
            return f"```python\n{code}\n```"
        
        text = re.sub(code_block_pattern, clean_code_block, text, flags=re.DOTALL)
        
        return text
    
    def extract_code_snippets(self, text: str) -> List[Dict]:
        """
        Extract code snippets from text
        """
        code_snippets = []
        
        # Pattern for code blocks
        code_block_pattern = r'```(?:python)?\n?(.*?)\n?```'
        matches = re.finditer(code_block_pattern, text, re.DOTALL)
        
        for match in matches:
            code = match.group(1).strip()
            if len(code) > 10:  # Only meaningful code snippets
                # Try to extract context around the code
                start_pos = max(0, match.start() - 200)
                end_pos = min(len(text), match.end() + 200)
                context = text[start_pos:end_pos]
                
                code_snippets.append({
                    'code': code,
                    'context': context,
                    'position': match.start(),
                    'type': 'python'
                })
        
        # Pattern for inline code
        inline_code_pattern = r'`([^`\n]+)`'
        matches = re.finditer(inline_code_pattern, text)
        
        for match in matches:
            code = match.group(1).strip()
            if len(code) > 5 and any(char in code for char in ['(', '.', '=']):
                # Looks like code
                start_pos = max(0, match.start() - 100)
                end_pos = min(len(text), match.end() + 100)
                context = text[start_pos:end_pos]
                
                code_snippets.append({
                    'code': code,
                    'context': context,
                    'position': match.start(),
                    'type': 'inline'
                })
        
        return code_snippets
    
    def validate_content_quality(self, content: str) -> Dict:
        """
        Validate and score content quality
        """
        if not content:
            return {'score': 0.0, 'issues': ['Empty content']}
        
        issues = []
        score = 1.0
        
        # Length checks
        content_length = len(content)
        if content_length < 50:
            issues.append('Content too short')
            score -= 0.3
        elif content_length > 50000:
            issues.append('Content too long')
            score -= 0.2
        
        # Language checks
        if not self._is_primarily_english(content):
            issues.append('Content not primarily in English')
            score -= 0.4
        
        # Structure checks
        sentences = [s.strip() for s in content.split('.') if len(s.strip()) > 10]
        if len(sentences) < 3:
            issues.append('Insufficient sentence structure')
            score -= 0.2
        
        # Python relevance
        python_keywords = ['python', 'def', 'class', 'import', 'function', 'variable']
        python_score = sum(1 for keyword in python_keywords if keyword.lower() in content.lower())
        if python_score == 0:
            issues.append('No Python-related content detected')
            score -= 0.3
        
        # Code presence
        code_snippets = self.extract_code_snippets(content)
        if not code_snippets:
            issues.append('No code examples found')
            score -= 0.2
        
        # Readability (simple heuristic)
        words = content.split()
        if len(words) > 0:
            avg_word_length = sum(len(word) for word in words) / len(words)
            if avg_word_length > 8:  # Very long words might indicate poor quality
                issues.append('Poor readability (complex vocabulary)')
                score -= 0.1
        
        return {
            'score': max(0.0, score),
            'issues': issues,
            'content_length': content_length,
            'sentence_count': len(sentences),
            'python_relevance': python_score,
            'code_snippets_count': len(code_snippets)
        }
    
    def _is_primarily_english(self, text: str) -> bool:
        """
        Check if text is primarily in English (simple heuristic)
        """
        # Count ASCII characters vs non-ASCII
        ascii_count = sum(1 for char in text if ord(char) < 128)
        total_count = len(text)
        
        if total_count == 0:
            return False
        
        ascii_ratio = ascii_count / total_count
        return ascii_ratio > 0.8  # 80% ASCII characters
    
    def clean_training_data(self, data_items: List[Dict]) -> List[Dict]:
        """
        Clean a list of training data items
        """
        cleaned_items = []
        
        for item in data_items:
            try:
                cleaned_item = item.copy()
                
                # Clean text fields
                if 'content' in cleaned_item:
                    cleaned_item['content'] = self.clean_text_content(cleaned_item['content'])
                
                if 'question' in cleaned_item:
                    cleaned_item['question'] = self.clean_text_content(cleaned_item['question'])
                
                if 'answer' in cleaned_item:
                    cleaned_item['answer'] = self.clean_text_content(cleaned_item['answer'])
                
                if 'title' in cleaned_item:
                    cleaned_item['title'] = self.clean_text_content(cleaned_item['title'])
                
                # Validate quality
                main_content = cleaned_item.get('content') or cleaned_item.get('answer') or ''
                quality_check = self.validate_content_quality(main_content)
                cleaned_item['quality_score'] = quality_check['score']
                cleaned_item['quality_issues'] = quality_check['issues']
                
                # Only keep items with acceptable quality
                if quality_check['score'] >= 0.3:  # Minimum quality threshold
                    cleaned_items.append(cleaned_item)
                else:
                    logger.debug(f"Filtered out low-quality item: {quality_check['issues']}")
                
            except Exception as e:
                logger.error(f"Error cleaning data item: {str(e)}")
                continue
        
        logger.info(f"Cleaned {len(cleaned_items)} items from {len(data_items)} original items")
        return cleaned_items
