import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import json
import re
from models import KnowledgeBase, TrainingData
from app import db
from data_processing.cleaner import DataCleaner

logger = logging.getLogger(__name__)

class DataProcessor:
    def __init__(self):
        self.cleaner = DataCleaner()
        
    def process_scraped_data(self, scraped_items: List[Dict]) -> Dict:
        """
        Process scraped data and store in database
        """
        logger.info(f"Processing {len(scraped_items)} scraped items")
        
        results = {
            'processed': 0,
            'knowledge_base_items': 0,
            'training_data_items': 0,
            'duplicates_skipped': 0,
            'low_quality_skipped': 0,
            'errors': 0
        }
        
        try:
            # Clean the data first
            cleaned_items = self.cleaner.clean_training_data(scraped_items)
            
            for item in cleaned_items:
                try:
                    # Check for duplicates
                    if self._is_duplicate_content(item):
                        results['duplicates_skipped'] += 1
                        continue
                    
                    # Check quality
                    if item.get('quality_score', 0) < 0.5:
                        results['low_quality_skipped'] += 1
                        continue
                    
                    # Process based on source type and structure
                    if self._is_qa_format(item):
                        # Process as training data (Q&A format)
                        if self._create_training_data(item):
                            results['training_data_items'] += 1
                    else:
                        # Process as knowledge base item
                        if self._create_knowledge_base_item(item):
                            results['knowledge_base_items'] += 1
                    
                    results['processed'] += 1
                    
                except Exception as e:
                    logger.error(f"Error processing individual item: {str(e)}")
                    results['errors'] += 1
                    continue
            
            # Commit all changes
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error processing scraped data: {str(e)}")
            db.session.rollback()
            results['errors'] += 1
        
        logger.info(f"Data processing completed: {results}")
        return results
    
    def _is_qa_format(self, item: Dict) -> bool:
        """
        Check if item is in Q&A format suitable for training data
        """
        return 'question' in item and 'answer' in item
    
    def _is_duplicate_content(self, item: Dict) -> bool:
        """
        Check if content already exists in database
        """
        try:
            content = item.get('content') or item.get('answer', '')
            url = item.get('source_url', '')
            
            if url:
                # Check by URL first
                existing = KnowledgeBase.query.filter_by(source_url=url).first()
                if existing:
                    return True
                
                # Check training data by URL
                existing_training = TrainingData.query.filter_by(source=url).first()
                if existing_training:
                    return True
            
            if content and len(content) > 100:
                # Check for similar content (simple approach - first 200 chars)
                content_sample = content[:200]
                
                existing = KnowledgeBase.query.filter(
                    KnowledgeBase.content.like(f"{content_sample}%")
                ).first()
                
                if existing:
                    return True
                
                existing_training = TrainingData.query.filter(
                    TrainingData.answer.like(f"{content_sample}%")
                ).first()
                
                if existing_training:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking for duplicates: {str(e)}")
            return False
    
    def _create_knowledge_base_item(self, item: Dict) -> bool:
        """
        Create a knowledge base item from processed data
        """
        try:
            kb_item = KnowledgeBase(
                title=item.get('title', 'Untitled'),
                content=item.get('content', ''),
                source_url=item.get('source_url'),
                source_type=item.get('source_type', 'unknown'),
                quality_score=item.get('quality_score', 0.0)
            )
            
            db.session.add(kb_item)
            return True
            
        except Exception as e:
            logger.error(f"Error creating knowledge base item: {str(e)}")
            return False
    
    def _create_training_data(self, item: Dict) -> bool:
        """
        Create training data from Q&A format item
        """
        try:
            training_item = TrainingData(
                question=item.get('question', ''),
                answer=item.get('answer', ''),
                source=item.get('source_url', ''),
                quality_score=item.get('quality_score', 0.0)
            )
            
            db.session.add(training_item)
            return True
            
        except Exception as e:
            logger.error(f"Error creating training data: {str(e)}")
            return False
    
    def extract_training_pairs(self, knowledge_base_items: List[Dict]) -> List[Dict]:
        """
        Extract question-answer pairs from knowledge base content
        """
        training_pairs = []
        
        for item in knowledge_base_items:
            try:
                content = item.get('content', '')
                pairs = self._generate_qa_pairs_from_content(content, item)
                training_pairs.extend(pairs)
                
            except Exception as e:
                logger.error(f"Error extracting training pairs: {str(e)}")
                continue
        
        logger.info(f"Extracted {len(training_pairs)} training pairs from knowledge base")
        return training_pairs
    
    def _generate_qa_pairs_from_content(self, content: str, source_item: Dict) -> List[Dict]:
        """
        Generate Q&A pairs from content using simple heuristics
        """
        pairs = []
        
        try:
            # Extract code examples and create Q&A pairs
            code_snippets = self.cleaner.extract_code_snippets(content)
            
            for snippet in code_snippets:
                if len(snippet['code']) > 20:  # Meaningful code
                    # Generate question based on code
                    question = self._generate_question_for_code(snippet['code'])
                    if question:
                        # Create answer with context
                        answer = f"{snippet['context']}\n\n```python\n{snippet['code']}\n```"
                        
                        pairs.append({
                            'question': question,
                            'answer': answer,
                            'source_url': source_item.get('source_url'),
                            'source_type': f"{source_item.get('source_type', 'unknown')}_generated",
                            'quality_score': source_item.get('quality_score', 0.5)
                        })
            
            # Extract FAQ-style content
            faq_pairs = self._extract_faq_pairs(content, source_item)
            pairs.extend(faq_pairs)
            
            # Extract definition-style content
            definition_pairs = self._extract_definition_pairs(content, source_item)
            pairs.extend(definition_pairs)
            
        except Exception as e:
            logger.error(f"Error generating Q&A pairs: {str(e)}")
        
        return pairs
    
    def _generate_question_for_code(self, code: str) -> Optional[str]:
        """
        Generate a question for a code snippet
        """
        try:
            # Simple patterns to generate questions
            if 'def ' in code:
                # Function definition
                func_match = re.search(r'def\s+(\w+)\s*\(([^)]*)\)', code)
                if func_match:
                    func_name = func_match.group(1)
                    return f"How do you implement the {func_name} function in Python?"
            
            if 'class ' in code:
                # Class definition
                class_match = re.search(r'class\s+(\w+)', code)
                if class_match:
                    class_name = class_match.group(1)
                    return f"How do you define a {class_name} class in Python?"
            
            if 'import ' in code:
                # Import statement
                return "How do you import modules in Python?"
            
            if any(keyword in code for keyword in ['for ', 'while ', 'if ']):
                # Control structures
                return "How do you use control structures in Python?"
            
            if '=' in code and not '==' in code:
                # Variable assignment
                return "How do you assign variables in Python?"
            
            # Generic question
            return "How do you write this Python code?"
            
        except Exception as e:
            logger.error(f"Error generating question for code: {str(e)}")
            return None
    
    def _extract_faq_pairs(self, content: str, source_item: Dict) -> List[Dict]:
        """
        Extract FAQ-style Q&A pairs from content
        """
        pairs = []
        
        try:
            # Look for question patterns
            question_patterns = [
                r'Q:\s*(.+?)\n\s*A:\s*(.+?)(?=\n\s*Q:|\n\s*$)',
                r'Question:\s*(.+?)\n\s*Answer:\s*(.+?)(?=\n\s*Question:|\n\s*$)',
                r'(\w+[?]+)\s*\n\s*(.+?)(?=\n\s*\w+[?]+|\n\s*$)',
            ]
            
            for pattern in question_patterns:
                matches = re.finditer(pattern, content, re.DOTALL | re.IGNORECASE)
                for match in matches:
                    question = match.group(1).strip()
                    answer = match.group(2).strip()
                    
                    if len(question) > 10 and len(answer) > 20:
                        pairs.append({
                            'question': question,
                            'answer': answer,
                            'source_url': source_item.get('source_url'),
                            'source_type': f"{source_item.get('source_type', 'unknown')}_faq",
                            'quality_score': source_item.get('quality_score', 0.5)
                        })
            
        except Exception as e:
            logger.error(f"Error extracting FAQ pairs: {str(e)}")
        
        return pairs
    
    def _extract_definition_pairs(self, content: str, source_item: Dict) -> List[Dict]:
        """
        Extract definition-style Q&A pairs
        """
        pairs = []
        
        try:
            # Look for definition patterns
            definition_patterns = [
                r'(\w+)\s+is\s+(.+?)(?=\n\n|\n\w+\s+is|\Z)',
                r'(\w+):\s*(.+?)(?=\n\w+:|\n\n|\Z)',
                r'The\s+(\w+)\s+(.+?)(?=\n\n|The\s+\w+|\Z)',
            ]
            
            for pattern in definition_patterns:
                matches = re.finditer(pattern, content, re.DOTALL)
                for match in matches:
                    term = match.group(1).strip()
                    definition = match.group(2).strip()
                    
                    if (len(term) > 2 and len(definition) > 30 and 
                        any(keyword in definition.lower() for keyword in ['python', 'function', 'variable', 'class', 'method'])):
                        
                        question = f"What is {term} in Python?"
                        answer = f"{term} {definition}"
                        
                        pairs.append({
                            'question': question,
                            'answer': answer,
                            'source_url': source_item.get('source_url'),
                            'source_type': f"{source_item.get('source_type', 'unknown')}_definition",
                            'quality_score': source_item.get('quality_score', 0.5)
                        })
            
        except Exception as e:
            logger.error(f"Error extracting definition pairs: {str(e)}")
        
        return pairs
    
    def get_training_data_for_model(self, limit: int = 1000, min_quality: float = 0.5) -> List[Dict]:
        """
        Get training data suitable for model training
        """
        try:
            # Get high-quality training data
            training_items = TrainingData.query.filter(
                TrainingData.quality_score >= min_quality,
                TrainingData.used_for_training == False
            ).order_by(TrainingData.quality_score.desc()).limit(limit).all()
            
            training_data = []
            for item in training_items:
                training_data.append({
                    'question': item.question,
                    'answer': item.answer,
                    'quality_score': item.quality_score,
                    'id': item.id
                })
            
            logger.info(f"Retrieved {len(training_data)} training items")
            return training_data
            
        except Exception as e:
            logger.error(f"Error getting training data: {str(e)}")
            return []
    
    def mark_training_data_used(self, training_ids: List[int]) -> bool:
        """
        Mark training data as used
        """
        try:
            TrainingData.query.filter(TrainingData.id.in_(training_ids)).update(
                {TrainingData.used_for_training: True}, synchronize_session=False
            )
            db.session.commit()
            logger.info(f"Marked {len(training_ids)} training items as used")
            return True
            
        except Exception as e:
            logger.error(f"Error marking training data as used: {str(e)}")
            db.session.rollback()
            return False
    
    def get_knowledge_base_stats(self) -> Dict:
        """
        Get statistics about the knowledge base
        """
        try:
            stats = {
                'total_items': KnowledgeBase.query.count(),
                'by_source_type': {},
                'avg_quality_score': 0.0,
                'total_training_data': TrainingData.query.count(),
                'unused_training_data': TrainingData.query.filter_by(used_for_training=False).count()
            }
            
            # Count by source type
            source_types = db.session.query(KnowledgeBase.source_type, db.func.count()).group_by(KnowledgeBase.source_type).all()
            for source_type, count in source_types:
                stats['by_source_type'][source_type or 'unknown'] = count
            
            # Average quality score
            avg_quality = db.session.query(db.func.avg(KnowledgeBase.quality_score)).scalar()
            stats['avg_quality_score'] = round(float(avg_quality or 0), 2)
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting knowledge base stats: {str(e)}")
            return {}
