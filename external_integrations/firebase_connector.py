"""
Firebase Real-time Database Connector for PyLearnAI

This module provides integration with Firebase Real-time Database
for storing and retrieving learning data, user interactions, and
application generation metrics.
"""

import requests
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class FirebaseConnector:
    """
    Connector for Firebase Real-time Database integration
    """
    
    def __init__(self, firebase_url: str):
        self.firebase_url = firebase_url.rstrip('/')
        self.session = requests.Session()
        logger.info(f"Firebase connector initialized with URL: {self.firebase_url}")
    
    def store_user_interaction(self, interaction_data: Dict[str, Any]) -> bool:
        """
        Store user interaction data in Firebase
        
        Args:
            interaction_data: Dictionary containing interaction details
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            endpoint = f"{self.firebase_url}/user_interactions.json"
            
            # Add timestamp if not present
            if 'timestamp' not in interaction_data:
                interaction_data['timestamp'] = datetime.utcnow().isoformat()
            
            response = self.session.post(endpoint, json=interaction_data)
            response.raise_for_status()
            
            logger.info(f"User interaction stored successfully: {response.json().get('name', 'unknown')}")
            return True
            
        except requests.RequestException as e:
            logger.error(f"Failed to store user interaction: {str(e)}")
            return False
    
    def store_generated_app(self, app_data: Dict[str, Any]) -> bool:
        """
        Store generated application metadata in Firebase
        
        Args:
            app_data: Dictionary containing app generation details
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            endpoint = f"{self.firebase_url}/generated_apps.json"
            
            # Add generation timestamp
            app_data['generated_at'] = datetime.utcnow().isoformat()
            
            response = self.session.post(endpoint, json=app_data)
            response.raise_for_status()
            
            logger.info(f"Generated app data stored: {app_data.get('app_type', 'unknown')}")
            return True
            
        except requests.RequestException as e:
            logger.error(f"Failed to store generated app data: {str(e)}")
            return False
    
    def store_learning_progress(self, progress_data: Dict[str, Any]) -> bool:
        """
        Store learning progress and model metrics
        
        Args:
            progress_data: Dictionary containing learning metrics
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            endpoint = f"{self.firebase_url}/learning_progress.json"
            
            progress_data['recorded_at'] = datetime.utcnow().isoformat()
            
            response = self.session.post(endpoint, json=progress_data)
            response.raise_for_status()
            
            logger.info("Learning progress stored successfully")
            return True
            
        except requests.RequestException as e:
            logger.error(f"Failed to store learning progress: {str(e)}")
            return False
    
    def get_popular_app_requests(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve most popular app generation requests
        
        Args:
            limit: Maximum number of results to return
            
        Returns:
            List of popular app requests
        """
        try:
            endpoint = f"{self.firebase_url}/generated_apps.json"
            response = self.session.get(endpoint)
            response.raise_for_status()
            
            data = response.json() or {}
            
            # Count app types
            app_counts = {}
            for app_id, app_data in data.items():
                app_type = app_data.get('app_type', 'unknown')
                app_counts[app_type] = app_counts.get(app_type, 0) + 1
            
            # Sort by popularity and return top results
            popular_apps = sorted(app_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
            
            return [{'app_type': app_type, 'count': count} for app_type, count in popular_apps]
            
        except requests.RequestException as e:
            logger.error(f"Failed to retrieve popular app requests: {str(e)}")
            return []
    
    def get_user_feedback_patterns(self) -> Dict[str, Any]:
        """
        Analyze user interaction patterns for learning improvements
        
        Returns:
            Dictionary containing usage patterns and insights
        """
        try:
            endpoint = f"{self.firebase_url}/user_interactions.json"
            response = self.session.get(endpoint)
            response.raise_for_status()
            
            data = response.json() or {}
            
            if not data:
                return {'total_interactions': 0, 'patterns': {}}
            
            # Analyze patterns
            question_types = {}
            satisfaction_scores = []
            
            for interaction_id, interaction in data.items():
                # Categorize question types
                question = interaction.get('question', '').lower()
                if any(word in question for word in ['create', 'make', 'build', 'generate']):
                    question_types['app_generation'] = question_types.get('app_generation', 0) + 1
                elif any(word in question for word in ['how', 'what', 'why']):
                    question_types['general_questions'] = question_types.get('general_questions', 0) + 1
                elif any(word in question for word in ['error', 'bug', 'fix', 'problem']):
                    question_types['debugging'] = question_types.get('debugging', 0) + 1
                else:
                    question_types['other'] = question_types.get('other', 0) + 1
                
                # Collect satisfaction if available
                if 'satisfaction' in interaction:
                    satisfaction_scores.append(interaction['satisfaction'])
            
            avg_satisfaction = sum(satisfaction_scores) / len(satisfaction_scores) if satisfaction_scores else 0
            
            return {
                'total_interactions': len(data),
                'question_patterns': question_types,
                'average_satisfaction': avg_satisfaction,
                'most_common_type': max(question_types.items(), key=lambda x: x[1])[0] if question_types else 'none'
            }
            
        except requests.RequestException as e:
            logger.error(f"Failed to analyze user feedback patterns: {str(e)}")
            return {'total_interactions': 0, 'patterns': {}, 'error': str(e)}
    
    def store_scraped_content(self, content_data: Dict[str, Any]) -> bool:
        """
        Store web-scraped learning content
        
        Args:
            content_data: Dictionary containing scraped content
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            endpoint = f"{self.firebase_url}/scraped_content.json"
            
            content_data['scraped_at'] = datetime.utcnow().isoformat()
            
            response = self.session.post(endpoint, json=content_data)
            response.raise_for_status()
            
            logger.info(f"Scraped content stored: {content_data.get('source', 'unknown')}")
            return True
            
        except requests.RequestException as e:
            logger.error(f"Failed to store scraped content: {str(e)}")
            return False
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """
        Get comprehensive learning insights from Firebase data
        
        Returns:
            Dictionary containing learning analytics and insights
        """
        try:
            insights = {
                'popular_apps': self.get_popular_app_requests(),
                'user_patterns': self.get_user_feedback_patterns(),
                'system_status': 'operational',
                'last_updated': datetime.utcnow().isoformat()
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to get learning insights: {str(e)}")
            return {
                'error': str(e),
                'system_status': 'error',
                'last_updated': datetime.utcnow().isoformat()
            }
    
    def test_connection(self) -> bool:
        """
        Test Firebase connection
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            test_data = {
                'test': True,
                'timestamp': datetime.utcnow().isoformat(),
                'message': 'PyLearnAI connection test'
            }
            
            endpoint = f"{self.firebase_url}/connection_test.json"
            response = self.session.post(endpoint, json=test_data)
            response.raise_for_status()
            
            logger.info("Firebase connection test successful")
            return True
            
        except requests.RequestException as e:
            logger.error(f"Firebase connection test failed: {str(e)}")
            return False

# Global Firebase connector instance
firebase_connector = None

def get_firebase_connector() -> Optional[FirebaseConnector]:
    """
    Get the global Firebase connector instance
    
    Returns:
        FirebaseConnector instance or None if not initialized
    """
    global firebase_connector
    
    if firebase_connector is None:
        firebase_url = "https://myaisystem-16411-default-rtdb.firebaseio.com/"
        firebase_connector = FirebaseConnector(firebase_url)
        
        # Test connection
        if firebase_connector.test_connection():
            logger.info("Firebase connector ready for use")
        else:
            logger.warning("Firebase connector initialized but connection test failed")
    
    return firebase_connector