import requests
import logging
import time
from typing import List, Dict, Optional
from config import Config
from scrapers.web_scraper import WebScraper
import json

logger = logging.getLogger(__name__)

class StackOverflowScraper(WebScraper):
    def __init__(self):
        super().__init__()
        self.api_key = Config.STACKOVERFLOW_API_KEY
        self.base_api_url = "https://api.stackexchange.com/2.3"
        self.tags = Config.STACKOVERFLOW_TAGS
        self.site = "stackoverflow"
        
    def scrape_stackoverflow_questions(self, max_questions: int = 100) -> List[Dict]:
        """
        Scrape Python-related questions and answers from Stack Overflow
        """
        logger.info("Starting Stack Overflow scraping")
        all_results = []
        
        for tag in self.tags:
            logger.info(f"Scraping questions for tag: {tag}")
            
            try:
                questions = self.get_questions_by_tag(tag, max_questions // len(self.tags))
                
                for question in questions:
                    # Get detailed question with answers
                    detailed_question = self.get_question_details(question['question_id'])
                    
                    if detailed_question:
                        processed_item = self.process_question_data(detailed_question)
                        if processed_item:
                            all_results.append(processed_item)
                
                # Rate limiting
                time.sleep(self.delay)
                
            except Exception as e:
                logger.error(f"Error scraping tag {tag}: {str(e)}")
                continue
        
        logger.info(f"Stack Overflow scraping completed. Total items: {len(all_results)}")
        return all_results
    
    def get_questions_by_tag(self, tag: str, max_count: int = 50) -> List[Dict]:
        """
        Get questions by tag using Stack Overflow API
        """
        try:
            params = {
                'site': self.site,
                'tagged': tag,
                'sort': 'votes',
                'order': 'desc',
                'pagesize': min(max_count, 100),  # API limit
                'filter': 'default'
            }
            
            if self.api_key:
                params['key'] = self.api_key
            
            response = requests.get(f"{self.base_api_url}/questions", params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            if 'items' not in data:
                logger.warning(f"No questions found for tag: {tag}")
                return []
            
            questions = []
            for item in data['items']:
                questions.append({
                    'question_id': item['question_id'],
                    'title': item['title'],
                    'score': item['score'],
                    'view_count': item.get('view_count', 0),
                    'answer_count': item.get('answer_count', 0),
                    'tags': item.get('tags', []),
                    'creation_date': item.get('creation_date'),
                    'link': item.get('link', '')
                })
            
            logger.info(f"Found {len(questions)} questions for tag: {tag}")
            return questions
            
        except requests.RequestException as e:
            logger.error(f"API request error for tag {tag}: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error getting questions for tag {tag}: {str(e)}")
            return []
    
    def get_question_details(self, question_id: int) -> Optional[Dict]:
        """
        Get detailed question data including answers
        """
        try:
            params = {
                'site': self.site,
                'filter': 'withbody'  # Include question and answer bodies
            }
            
            if self.api_key:
                params['key'] = self.api_key
            
            # Get question details
            question_response = requests.get(
                f"{self.base_api_url}/questions/{question_id}",
                params=params,
                timeout=self.timeout
            )
            question_response.raise_for_status()
            question_data = question_response.json()
            
            if not question_data.get('items'):
                return None
            
            question = question_data['items'][0]
            
            # Get answers for the question
            answers_response = requests.get(
                f"{self.base_api_url}/questions/{question_id}/answers",
                params=params,
                timeout=self.timeout
            )
            answers_response.raise_for_status()
            answers_data = answers_response.json()
            
            question['answers'] = answers_data.get('items', [])
            
            # Rate limiting
            time.sleep(0.1)  # Additional delay for API calls
            
            return question
            
        except requests.RequestException as e:
            logger.error(f"API request error for question {question_id}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error getting question details for {question_id}: {str(e)}")
            return None
    
    def process_question_data(self, question_data: Dict) -> Optional[Dict]:
        """
        Process raw question data into structured format for training
        """
        try:
            question_title = question_data.get('title', '')
            question_body = question_data.get('body', '')
            question_score = question_data.get('score', 0)
            
            # Combine question title and body
            full_question = f"{question_title}\n\n{question_body}"
            
            # Clean HTML from question
            question_text = self._clean_html_content(full_question)
            
            if len(question_text) < 50:  # Skip very short questions
                return None
            
            # Find the best answer (highest score, or accepted)
            best_answer = self._find_best_answer(question_data.get('answers', []))
            
            if not best_answer:
                return None
            
            answer_text = self._clean_html_content(best_answer['body'])
            
            if len(answer_text) < 30:  # Skip very short answers
                return None
            
            # Calculate quality score
            quality_score = self._calculate_stackoverflow_quality(
                question_score,
                best_answer.get('score', 0),
                question_data.get('view_count', 0),
                question_text,
                answer_text
            )
            
            if quality_score < Config.MIN_QUALITY_SCORE:
                return None
            
            return {
                'question': question_text,
                'answer': answer_text,
                'source_url': question_data.get('link', ''),
                'source_type': 'stackoverflow',
                'tags': question_data.get('tags', []),
                'question_score': question_score,
                'answer_score': best_answer.get('score', 0),
                'view_count': question_data.get('view_count', 0),
                'quality_score': quality_score,
                'scraped_at': time.time()
            }
            
        except Exception as e:
            logger.error(f"Error processing question data: {str(e)}")
            return None
    
    def _find_best_answer(self, answers: List[Dict]) -> Optional[Dict]:
        """
        Find the best answer from a list of answers
        """
        if not answers:
            return None
        
        # First, look for accepted answer
        for answer in answers:
            if answer.get('is_accepted', False):
                return answer
        
        # If no accepted answer, find highest scored answer
        best_answer = max(answers, key=lambda x: x.get('score', 0))
        
        # Only return if it has a positive score
        if best_answer.get('score', 0) > 0:
            return best_answer
        
        return None
    
    def _clean_html_content(self, html_content: str) -> str:
        """
        Clean HTML content and convert to readable text
        """
        try:
            from bs4 import BeautifulSoup
            import re
            
            if not html_content:
                return ""
            
            # Parse HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Convert code blocks to readable format
            for code_block in soup.find_all('code'):
                code_text = code_block.get_text()
                code_block.replace_with(f"\n```python\n{code_text}\n```\n")
            
            # Get text content
            text = soup.get_text()
            
            # Clean up whitespace
            text = re.sub(r'\s+', ' ', text)
            text = re.sub(r'\n\s*\n', '\n\n', text)
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error cleaning HTML content: {str(e)}")
            return html_content  # Return original if cleaning fails
    
    def _calculate_stackoverflow_quality(self, question_score: int, answer_score: int, 
                                       view_count: int, question_text: str, answer_text: str) -> float:
        """
        Calculate quality score for Stack Overflow content
        """
        score = 0.0
        
        # Score based on votes
        if question_score > 0:
            score += min(question_score * 0.1, 0.3)
        if answer_score > 0:
            score += min(answer_score * 0.1, 0.4)
        
        # Score based on view count (popular questions are often better)
        if view_count > 1000:
            score += 0.2
        elif view_count > 100:
            score += 0.1
        
        # Content quality checks
        if any(keyword in question_text.lower() for keyword in ['python', 'def', 'class', 'import']):
            score += 0.1
        
        if any(keyword in answer_text.lower() for keyword in ['def', 'class', 'import', '```']):
            score += 0.2
        
        # Length checks
        if 100 <= len(question_text) <= 2000 and 50 <= len(answer_text) <= 3000:
            score += 0.1
        
        return min(score, 1.0)
    
    def scrape_by_search_query(self, query: str, max_results: int = 50) -> List[Dict]:
        """
        Search Stack Overflow by query and scrape results
        """
        try:
            params = {
                'site': self.site,
                'q': query,
                'sort': 'relevance',
                'order': 'desc',
                'pagesize': min(max_results, 100),
                'filter': 'default'
            }
            
            if self.api_key:
                params['key'] = self.api_key
            
            response = requests.get(f"{self.base_api_url}/search", params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for item in data.get('items', []):
                detailed_question = self.get_question_details(item['question_id'])
                if detailed_question:
                    processed_item = self.process_question_data(detailed_question)
                    if processed_item:
                        results.append(processed_item)
            
            logger.info(f"Found {len(results)} results for query: {query}")
            return results
            
        except Exception as e:
            logger.error(f"Error searching Stack Overflow for query '{query}': {str(e)}")
            return []
