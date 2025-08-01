import re
import html
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from urllib.parse import urlparse, parse_qs
import logging

logger = logging.getLogger(__name__)

def format_datetime(dt: Optional[datetime], format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format a datetime object to a string
    
    Args:
        dt: DateTime object to format
        format_str: Format string for strftime
        
    Returns:
        Formatted datetime string or 'Unknown' if dt is None
    """
    if dt is None:
        return "Unknown"
    
    try:
        # Ensure timezone awareness
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        
        return dt.strftime(format_str)
    except Exception as e:
        logger.error(f"Error formatting datetime {dt}: {str(e)}")
        return "Invalid Date"

def format_relative_time(dt: Optional[datetime]) -> str:
    """
    Format datetime as relative time (e.g., '2 hours ago')
    
    Args:
        dt: DateTime object to format
        
    Returns:
        Relative time string
    """
    if dt is None:
        return "Unknown"
    
    try:
        now = datetime.utcnow()
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        
        now = now.replace(tzinfo=timezone.utc)
        
        diff = now - dt
        seconds = diff.total_seconds()
        
        if seconds < 60:
            return "Just now"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        elif seconds < 86400:
            hours = int(seconds // 3600)
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif seconds < 2592000:  # 30 days
            days = int(seconds // 86400)
            return f"{days} day{'s' if days != 1 else ''} ago"
        else:
            return dt.strftime("%Y-%m-%d")
            
    except Exception as e:
        logger.error(f"Error formatting relative time {dt}: {str(e)}")
        return "Unknown"

def sanitize_input(text: str, max_length: int = 10000) -> str:
    """
    Sanitize user input text
    
    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Convert to string if not already
    text = str(text)
    
    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length]
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Unescape HTML entities
    text = html.unescape(text)
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text

def sanitize_html(text: str) -> str:
    """
    Escape HTML characters in text
    
    Args:
        text: Text to escape
        
    Returns:
        HTML-escaped text
    """
    if not text:
        return ""
    
    return html.escape(str(text))

def validate_question(question: str) -> bool:
    """
    Validate if a question is acceptable for processing
    
    Args:
        question: The question to validate
        
    Returns:
        True if question is valid, False otherwise
    """
    if not question or not question.strip():
        return False
    
    # Remove excessive length restriction and allow conversational inputs
    if len(question.strip()) > 5000:  # Very generous limit
        return False
    
    # Allow almost all characters and patterns - be very permissive for conversational AI
    # Only block obvious spam or malicious patterns
    blocked_patterns = [
        r'(.)\1{20,}',  # Repeated character spam (20+ times)
        r'[<>]{5,}',    # HTML/XML injection attempts
        r'script\s*:',  # Script injection
        r'javascript\s*:',  # JavaScript injection
    ]
    
    question_lower = question.lower().strip()
    
    for pattern in blocked_patterns:
        if re.search(pattern, question_lower, re.IGNORECASE):
            return False
    
    # Accept everything else including simple greetings like "hi", "hello", etc.
    return True

def validate_url(url: str) -> bool:
    """
    Validate a URL
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not url or not isinstance(url, str):
        return False
    
    try:
        parsed = urlparse(url)
        return all([parsed.scheme, parsed.netloc])
    except Exception:
        return False

def extract_domain(url: str) -> Optional[str]:
    """
    Extract domain from URL
    
    Args:
        url: URL to extract domain from
        
    Returns:
        Domain string or None if invalid
    """
    try:
        parsed = urlparse(url)
        return parsed.netloc.lower()
    except Exception:
        return None

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to specified length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if not text:
        return ""
    
    text = str(text)
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    
    return f"{s} {size_names[i]}"

def parse_query_params(query_string: str) -> Dict[str, str]:
    """
    Parse query string parameters
    
    Args:
        query_string: Query string to parse
        
    Returns:
        Dictionary of parameters
    """
    try:
        params = parse_qs(query_string)
        # Convert lists to single values
        return {k: v[0] if v else '' for k, v in params.items()}
    except Exception:
        return {}

def clean_filename(filename: str) -> str:
    """
    Clean filename for safe filesystem storage
    
    Args:
        filename: Original filename
        
    Returns:
        Cleaned filename
    """
    if not filename:
        return "untitled"
    
    # Remove path separators and dangerous characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove control characters
    filename = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', filename)
    
    # Limit length
    if len(filename) > 200:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:190] + ('.' + ext if ext else '')
    
    # Ensure not empty
    if not filename or filename == '.':
        return "untitled"
    
    return filename

def generate_slug(text: str, max_length: int = 50) -> str:
    """
    Generate URL-friendly slug from text
    
    Args:
        text: Text to convert to slug
        max_length: Maximum slug length
        
    Returns:
        URL-friendly slug
    """
    if not text:
        return "untitled"
    
    # Convert to lowercase
    slug = text.lower()
    
    # Replace spaces and special characters with hyphens
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    
    # Limit length
    if len(slug) > max_length:
        slug = slug[:max_length].rstrip('-')
    
    # Ensure not empty
    if not slug:
        return "untitled"
    
    return slug

def calculate_quality_score(content: str, factors: Dict[str, Any]) -> float:
    """
    Calculate quality score for content based on various factors
    
    Args:
        content: Content to analyze
        factors: Dictionary of quality factors
        
    Returns:
        Quality score between 0.0 and 1.0
    """
    if not content:
        return 0.0
    
    score = 0.0
    
    # Length factor
    content_length = len(content)
    if 100 <= content_length <= 5000:
        score += 0.2
    elif 50 <= content_length < 100 or 5000 < content_length <= 10000:
        score += 0.1
    
    # Python relevance
    python_keywords = ['python', 'def', 'class', 'import', 'function', 'variable', 'list', 'dict']
    keyword_count = sum(1 for keyword in python_keywords if keyword.lower() in content.lower())
    score += min(keyword_count * 0.05, 0.3)
    
    # Code examples
    if '```' in content or 'def ' in content or 'import ' in content:
        score += 0.2
    
    # Readability (sentence structure)
    sentences = [s.strip() for s in content.split('.') if len(s.strip()) > 10]
    if len(sentences) >= 3:
        score += 0.2
    
    # External factors
    if factors:
        # User rating factor
        if 'user_rating' in factors and factors['user_rating']:
            rating_score = factors['user_rating'] / 5.0
            score += rating_score * 0.1
        
        # Source credibility
        if 'source_type' in factors:
            source_scores = {
                'python_docs': 0.9,
                'stackoverflow': 0.8,
                'github': 0.7,
                'generated': 0.5
            }
            source_type = factors['source_type']
            if source_type in source_scores:
                score *= source_scores[source_type]
    
    return min(max(score, 0.0), 1.0)

def extract_code_blocks(text: str) -> List[Dict[str, str]]:
    """
    Extract code blocks from text
    
    Args:
        text: Text containing code blocks
        
    Returns:
        List of code block dictionaries
    """
    code_blocks = []
    
    # Pattern for fenced code blocks
    fenced_pattern = r'```(?:python)?\n?(.*?)\n?```'
    matches = re.finditer(fenced_pattern, text, re.DOTALL)
    
    for match in matches:
        code = match.group(1).strip()
        if len(code) > 10:  # Only meaningful code blocks
            code_blocks.append({
                'code': code,
                'language': 'python',
                'type': 'fenced'
            })
    
    # Pattern for inline code
    inline_pattern = r'`([^`\n]+)`'
    matches = re.finditer(inline_pattern, text)
    
    for match in matches:
        code = match.group(1).strip()
        if len(code) > 5 and any(char in code for char in ['(', '.', '=']):
            code_blocks.append({
                'code': code,
                'language': 'python',
                'type': 'inline'
            })
    
    return code_blocks

def is_python_related(text: str) -> bool:
    """
    Check if text is Python-related
    
    Args:
        text: Text to analyze
        
    Returns:
        True if Python-related, False otherwise
    """
    if not text:
        return False
    
    text_lower = text.lower()
    
    # Strong Python indicators
    strong_indicators = ['python', 'py', 'def ', 'import ', 'class ', '__init__', 'pip ', 'conda']
    strong_count = sum(1 for indicator in strong_indicators if indicator in text_lower)
    
    if strong_count >= 2:
        return True
    
    # Python-specific patterns
    python_patterns = [
        r'\bdef\s+\w+\s*\(',
        r'\bclass\s+\w+\s*:',
        r'\bimport\s+\w+',
        r'\bfrom\s+\w+\s+import',
        r'\.py\b',
        r'python\s*\d+',
        r'pip\s+install',
        r'__\w+__'
    ]
    
    pattern_matches = sum(1 for pattern in python_patterns if re.search(pattern, text_lower))
    
    return pattern_matches >= 1

def format_code_snippet(code: str, language: str = 'python') -> str:
    """
    Format code snippet with proper indentation and syntax
    
    Args:
        code: Code to format
        language: Programming language
        
    Returns:
        Formatted code string
    """
    if not code:
        return ""
    
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
            formatted_lines = []
            for line in lines:
                if line.strip():
                    formatted_lines.append(line[min_indent:])
                else:
                    formatted_lines.append(line)
            code = '\n'.join(formatted_lines)
    
    return code.strip()

def validate_api_key(api_key: str, service: str) -> bool:
    """
    Validate API key format for different services
    
    Args:
        api_key: API key to validate
        service: Service name (github, stackoverflow, etc.)
        
    Returns:
        True if format is valid, False otherwise
    """
    if not api_key or not isinstance(api_key, str):
        return False
    
    # Basic length and character checks
    if len(api_key) < 10:
        return False
    
    # Service-specific validation
    if service.lower() == 'github':
        # GitHub tokens are typically 40 characters, alphanumeric
        return bool(re.match(r'^[a-zA-Z0-9]{20,}$', api_key))
    
    elif service.lower() == 'stackoverflow':
        # Stack Overflow keys are typically alphanumeric with some special chars
        return bool(re.match(r'^[a-zA-Z0-9){(*&^%$#@!+=]{8,}$', api_key))
    
    # Generic validation for other services
    return bool(re.match(r'^[a-zA-Z0-9\-_\.]{8,}$', api_key))

def safe_division(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Perform safe division with default fallback
    
    Args:
        numerator: Numerator value
        denominator: Denominator value
        default: Default value if division by zero
        
    Returns:
        Division result or default value
    """
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except (TypeError, ValueError):
        return default

def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split a list into chunks of specified size
    
    Args:
        lst: List to chunk
        chunk_size: Size of each chunk
        
    Returns:
        List of chunks
    """
    chunks = []
    for i in range(0, len(lst), chunk_size):
        chunks.append(lst[i:i + chunk_size])
    return chunks

def merge_dictionaries(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge multiple dictionaries, with later ones taking precedence
    
    Args:
        *dicts: Dictionaries to merge
        
    Returns:
        Merged dictionary
    """
    result = {}
    for d in dicts:
        if isinstance(d, dict):
            result.update(d)
    return result

def get_nested_value(data: Dict[str, Any], path: str, default: Any = None) -> Any:
    """
    Get nested value from dictionary using dot notation
    
    Args:
        data: Dictionary to search
        path: Dot-separated path (e.g., 'user.profile.name')
        default: Default value if path not found
        
    Returns:
        Found value or default
    """
    try:
        keys = path.split('.')
        value = data
        for key in keys:
            value = value[key]
        return value
    except (KeyError, TypeError):
        return default
