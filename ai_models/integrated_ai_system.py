"""
Integrated AI System
Combines all AI components for comprehensive programming assistance
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

# Import all AI components
from .enhanced_multi_language_ai import enhanced_ai
from .ml_training_system import MLTrainingSystem
from .web_framework_expert import web_expert
from .self_troubleshooting_ai import troubleshooting_ai
from .openai_enhanced_ai import openai_ai
from .multi_model_ai import multi_model_ai

logger = logging.getLogger(__name__)

class IntegratedAISystem:
    """
    Master AI system that integrates all specialized AI components
    """
    
    def __init__(self):
        self.enhanced_ai = enhanced_ai
        self.ml_system = MLTrainingSystem()
        self.web_expert = web_expert
        self.troubleshooting_ai = troubleshooting_ai
        self.openai_ai = openai_ai
        self.multi_model_ai = multi_model_ai
        
        # Component availability
        self.components = {
            'enhanced_multi_language': True,
            'ml_training': True,
            'web_framework_expert': True,
            'self_troubleshooting': True,
            'openai_enhanced': bool(self.openai_ai.openai_client),
            'multi_model_ai': bool(self.multi_model_ai.openai_client or self.multi_model_ai.deepseek_available),
            'deepseek_available': self.multi_model_ai.deepseek_available
        }
        
        logger.info(f"Integrated AI System initialized with components: {self.components}")
    
    def process_query(self, query: str, language: str = None, context: str = "",
                     request_type: str = "general") -> Dict:
        """
        Process query through the most appropriate AI component
        """
        # Auto-detect language if not provided
        if not language:
            language = self._detect_language_from_query(query)
        
        # Determine the best AI component for this query
        component = self._select_best_component(query, language, request_type)
        
        try:
            if component == 'openai_enhanced' and self.components['openai_enhanced']:
                return self._process_with_openai(query, language, context, request_type)
            elif component == 'troubleshooting' and 'error' in query.lower():
                return self._process_with_troubleshooting(query, language, context)
            elif component == 'web_expert' and language in ['html', 'css', 'javascript', 'react']:
                return self._process_with_web_expert(query, language, context)
            else:
                return self._process_with_enhanced_ai(query, language, context)
                
        except Exception as e:
            logger.error(f"Error processing query with {component}: {str(e)}")
            return self._fallback_response(query, language, context)
    
    def _detect_language_from_query(self, query: str) -> str:
        """Detect programming language from query"""
        query_lower = query.lower()
        
        # Specific framework detection
        if any(word in query_lower for word in ['react', 'jsx', 'usestate', 'useeffect']):
            return 'react'
        elif any(word in query_lower for word in ['vue', 'vuejs', 'nuxt']):
            return 'vue'
        elif any(word in query_lower for word in ['angular', 'typescript']):
            return 'angular'
        elif any(word in query_lower for word in ['flask', 'django', 'fastapi']):
            return 'python'
        elif any(word in query_lower for word in ['node', 'express', 'npm']):
            return 'javascript'
        elif any(word in query_lower for word in ['css', 'styling', 'layout', 'flexbox', 'grid']):
            return 'css'
        elif any(word in query_lower for word in ['html', 'markup', 'semantic']):
            return 'html'
        elif any(word in query_lower for word in ['python', 'pip', 'pandas', 'numpy']):
            return 'python'
        elif any(word in query_lower for word in ['javascript', 'js', 'es6', 'async']):
            return 'javascript'
        else:
            return 'general'
    
    def _select_best_component(self, query: str, language: str, request_type: str) -> str:
        """Select the best AI component for the query"""
        query_lower = query.lower()
        
        # Error handling and debugging
        if any(word in query_lower for word in ['error', 'bug', 'fix', 'debug', 'troubleshoot']):
            return 'troubleshooting'
        
        # Code generation and complex requests
        if any(word in query_lower for word in ['create', 'generate', 'build', 'implement']) and self.components['openai_enhanced']:
            return 'openai_enhanced'
        
        # Web-specific queries
        if language in ['html', 'css', 'javascript', 'react', 'vue', 'angular']:
            return 'web_expert'
        
        # Learning and tutorials
        if any(word in query_lower for word in ['learn', 'tutorial', 'how to', 'explain']) and self.components['openai_enhanced']:
            return 'openai_enhanced'
        
        # Default to enhanced AI
        return 'enhanced_ai'
    
    def _process_with_openai(self, query: str, language: str, context: str, request_type: str) -> Dict:
        """Process query with OpenAI enhanced AI"""
        response = self.openai_ai.generate_enhanced_response(query, language, context, request_type)
        
        # Add system metadata
        response['component_used'] = 'openai_enhanced'
        response['capabilities'] = ['advanced_generation', 'debugging', 'learning', 'architecture']
        
        return response
    
    def _process_with_troubleshooting(self, query: str, language: str, context: str) -> Dict:
        """Process query with troubleshooting AI"""
        # Extract error message from query if possible
        error_message = self._extract_error_from_query(query)
        
        diagnosis = self.troubleshooting_ai.auto_diagnose_error(
            error_message, context, language
        )
        
        return {
            'component_used': 'troubleshooting',
            'response': self._format_troubleshooting_response(diagnosis),
            'diagnosis': diagnosis,
            'language': language,
            'capabilities': ['error_diagnosis', 'auto_fixing', 'prevention_tips']
        }
    
    def _process_with_web_expert(self, query: str, language: str, context: str) -> Dict:
        """Process query with web framework expert"""
        # Analyze the query type
        if 'analyze' in query.lower() and context:
            analysis = self.web_expert.analyze_web_code(context, language)
            response = self._format_web_analysis_response(analysis, language)
        else:
            suggestions = self.web_expert.get_framework_suggestions(language, query)
            response = self._format_web_suggestions_response(suggestions, language)
        
        return {
            'component_used': 'web_expert',
            'response': response,
            'language': language,
            'capabilities': ['framework_patterns', 'performance_tips', 'component_generation']
        }
    
    def _process_with_enhanced_ai(self, query: str, language: str, context: str) -> Dict:
        """Process query with enhanced multi-language AI"""
        response = self.enhanced_ai.generate_comprehensive_response(query, language, context)
        
        return {
            'component_used': 'enhanced_multi_language',
            'response': response,
            'language': language,
            'capabilities': ['pattern_recognition', 'code_analysis', 'suggestions']
        }
    
    def _extract_error_from_query(self, query: str) -> str:
        """Extract error message from user query"""
        # Look for common error patterns
        import re
        
        error_patterns = [
            r'error[:\s](.+?)(?:\n|$)',
            r'exception[:\s](.+?)(?:\n|$)',
            r'failed[:\s](.+?)(?:\n|$)',
            r'cannot[:\s](.+?)(?:\n|$)',
            r'undefined[:\s](.+?)(?:\n|$)'
        ]
        
        for pattern in error_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return query  # Return full query if no specific error found
    
    def _format_troubleshooting_response(self, diagnosis: Dict) -> str:
        """Format troubleshooting response for user"""
        response = f"## Error Diagnosis (Confidence: {diagnosis['confidence']:.1%})\n\n"
        response += f"**Error Type:** {diagnosis['error_type']}\n"
        response += f"**Estimated Fix Time:** {diagnosis['estimated_fix_time']}\n\n"
        
        if diagnosis['solutions']:
            response += "## Solutions:\n"
            for i, solution in enumerate(diagnosis['solutions'], 1):
                response += f"{i}. {solution}\n"
            response += "\n"
        
        if diagnosis['code_fixes']:
            response += "## Code Fixes:\n"
            for fix in diagnosis['code_fixes']:
                response += f"```\n{fix}\n```\n"
        
        if diagnosis['prevention_tips']:
            response += "## Prevention Tips:\n"
            for tip in diagnosis['prevention_tips']:
                response += f"• {tip}\n"
        
        return response
    
    def _format_web_analysis_response(self, analysis: Dict, language: str) -> str:
        """Format web code analysis response"""
        response = f"## {language.title()} Code Analysis\n\n"
        
        if analysis.get('issues'):
            response += "### Issues Found:\n"
            for issue in analysis['issues']:
                response += f"❌ {issue}\n"
            response += "\n"
        
        if analysis.get('suggestions'):
            response += "### Suggestions:\n"
            for suggestion in analysis['suggestions']:
                response += f"💡 {suggestion}\n"
            response += "\n"
        
        if analysis.get('best_practices'):
            response += "### Best Practices:\n"
            for practice in analysis['best_practices']:
                response += f"✅ {practice}\n"
            response += "\n"
        
        if analysis.get('performance_tips'):
            response += "### Performance Tips:\n"
            for tip in analysis['performance_tips']:
                response += f"⚡ {tip}\n"
        
        return response
    
    def _format_web_suggestions_response(self, suggestions: List[Dict], language: str) -> str:
        """Format web framework suggestions response"""
        response = f"## {language.title()} Framework Guidance\n\n"
        
        for suggestion in suggestions[:5]:  # Limit to top 5 suggestions
            response += f"### {suggestion['name'].replace('_', ' ').title()}\n"
            
            if suggestion.get('description'):
                response += f"{suggestion['description']}\n\n"
            
            if suggestion.get('pattern'):
                response += f"**Pattern:**\n```{language}\n{suggestion['pattern']}\n```\n\n"
            
            if suggestion.get('code'):
                response += f"**Example:**\n```{language}\n{suggestion['code']}\n```\n\n"
            
            if suggestion.get('best_practices'):
                response += "**Best Practices:**\n"
                for practice in suggestion['best_practices'][:3]:
                    response += f"• {practice}\n"
                response += "\n"
        
        return response
    
    def _fallback_response(self, query: str, language: str, context: str) -> Dict:
        """Fallback response when all components fail"""
        return {
            'component_used': 'fallback',
            'response': f"I apologize, but I'm having difficulty processing your {language} question right now. Please try rephrasing your query or check if all required information is provided.",
            'language': language,
            'capabilities': ['basic_response']
        }
    
    def generate_code_with_full_support(self, description: str, language: str,
                                       complexity: str = "intermediate",
                                       include_tests: bool = True) -> Dict:
        """
        Generate code with full AI system support
        """
        # Use OpenAI for advanced code generation if available
        if self.components['openai_enhanced']:
            result = self.openai_ai.generate_code_with_tests(description, language, complexity)
        else:
            result = self._fallback_code_generation(description, language, complexity)
        
        # Enhance with web expert knowledge for web technologies
        if language in ['html', 'css', 'javascript', 'react']:
            web_suggestions = self.web_expert.get_framework_suggestions(language, description)
            result['framework_suggestions'] = web_suggestions[:3]
        
        # Add ML training sample for future improvement
        self.ml_system.add_training_sample(
            f"Generate {language} code: {description}",
            result['code'],
            language,
            'code_generation',
            0.8
        )
        
        return result
    
    def comprehensive_debug_assistance(self, code: str, error_message: str,
                                     language: str, context: str = "") -> Dict:
        """
        Comprehensive debugging with multiple AI systems
        """
        results = {}
        
        # Get troubleshooting AI diagnosis
        troubleshooting_result = self.troubleshooting_ai.auto_diagnose_error(
            error_message, context, language
        )
        results['troubleshooting'] = troubleshooting_result
        
        # Get OpenAI debugging assistance if available
        if self.components['openai_enhanced']:
            openai_result = self.openai_ai.debug_code_intelligently(
                code, error_message, language, context
            )
            results['openai_analysis'] = openai_result
        
        # Get web expert analysis for web technologies
        if language in ['html', 'css', 'javascript', 'react']:
            web_analysis = self.web_expert.analyze_web_code(code, language)
            results['web_analysis'] = web_analysis
        
        # Combine results for comprehensive response
        combined_response = self._combine_debug_results(results, language)
        
        return {
            'component_used': 'integrated_debugging',
            'response': combined_response,
            'detailed_results': results,
            'language': language,
            'capabilities': ['multi_system_analysis', 'comprehensive_debugging']
        }
    
    def _combine_debug_results(self, results: Dict, language: str) -> str:
        """Combine debugging results from multiple AI systems"""
        response = f"## Comprehensive {language.title()} Debug Analysis\n\n"
        
        # Troubleshooting AI results
        if 'troubleshooting' in results:
            t_result = results['troubleshooting']
            response += f"### Automated Diagnosis (Confidence: {t_result['confidence']:.1%})\n"
            response += f"**Error Type:** {t_result['error_type']}\n"
            response += f"**Estimated Fix Time:** {t_result['estimated_fix_time']}\n\n"
        
        # OpenAI analysis
        if 'openai_analysis' in results:
            oa_result = results['openai_analysis']
            response += "### AI-Powered Analysis\n"
            response += f"{oa_result['debug_analysis']}\n\n"
        
        # Web expert analysis
        if 'web_analysis' in results:
            wa_result = results['web_analysis']
            if wa_result.get('issues'):
                response += "### Framework-Specific Issues\n"
                for issue in wa_result['issues']:
                    response += f"⚠️ {issue}\n"
                response += "\n"
        
        response += "### Recommended Action Plan\n"
        response += "1. Review the automated diagnosis above\n"
        response += "2. Apply the suggested code fixes\n"
        response += "3. Test incrementally\n"
        response += "4. Implement prevention strategies\n"
        
        return response
    
    def _fallback_code_generation(self, description: str, language: str, complexity: str) -> Dict:
        """Fallback code generation when OpenAI is not available"""
        template_code = f"""
# {language.title()} code for: {description}
# Complexity level: {complexity}
# TODO: Implement the requested functionality

def main():
    # Your implementation here
    pass

if __name__ == "__main__":
    main()
        """
        
        return {
            'code': template_code.strip(),
            'language': language,
            'complexity': complexity,
            'tokens_used': 0,
            'includes_tests': False,
            'includes_docs': True,
            'note': 'This is a basic template. Enhanced generation requires OpenAI API access.'
        }
    
    def get_system_status(self) -> Dict:
        """Get comprehensive system status"""
        status = {
            'timestamp': datetime.now().isoformat(),
            'components': self.components,
            'capabilities': {
                'code_generation': self.components['openai_enhanced'],
                'advanced_debugging': True,
                'web_framework_support': True,
                'machine_learning': True,
                'self_troubleshooting': True,
                'multi_language_support': True
            },
            'performance_metrics': {}
        }
        
        # Add performance metrics if available
        try:
            if self.components['openai_enhanced']:
                status['performance_metrics']['openai'] = self.openai_ai.get_ai_insights()
        except Exception as e:
            logger.error(f"Error getting performance metrics: {str(e)}")
        
        return status

# Initialize integrated AI system
integrated_ai = IntegratedAISystem()