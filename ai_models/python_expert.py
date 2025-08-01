import logging
import os
import json
import time
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Try to import ML dependencies, fall back to simple expert if not available
try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments, TextDataset, DataCollatorForLanguageModeling
    from config import Config
    ML_AVAILABLE = True
except ImportError as e:
    logger.warning(f"ML dependencies not available: {e}. Using simple expert.")
    ML_AVAILABLE = False
    from ai_models.simple_expert import SimplePythonExpert

class PythonExpertAI:
    def __init__(self):
        if ML_AVAILABLE:
            self.model_name = Config.MODEL_NAME
            self.cache_dir = Config.MODEL_CACHE_DIR
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.tokenizer = None
            self.model = None
            self.load_model()
        else:
            self.simple_expert = SimplePythonExpert()
            logger.info("Using SimplePythonExpert as fallback")
    
    def load_model(self):
        """Load the pre-trained model and tokenizer"""
        if not ML_AVAILABLE:
            return  # Simple expert doesn't need model loading
        try:
            logger.info(f"Loading model {self.model_name}")
            
            # Create cache directory if it doesn't exist
            os.makedirs(self.cache_dir, exist_ok=True)
            
            # Load tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                cache_dir=self.cache_dir,
                pad_token='<|endoftext|>'
            )
            
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                cache_dir=self.cache_dir
            )
            
            # Add special tokens for Python context
            special_tokens = {
                "additional_special_tokens": [
                    "[PYTHON]", "[QUESTION]", "[ANSWER]", "[CODE]", "[EXPLANATION]"
                ]
            }
            
            num_added_tokens = self.tokenizer.add_special_tokens(special_tokens)
            if num_added_tokens > 0:
                self.model.resize_token_embeddings(len(self.tokenizer))
            
            self.model.to(self.device)
            logger.info(f"Model loaded successfully on device: {self.device}")
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise
    
    def generate_response(self, question, max_length=None):
        """Generate a response to a Python-related question"""
        if not ML_AVAILABLE:
            return self.simple_expert.generate_response(question, max_length or 500)
        
        try:
            start_time = time.time()
            
            if max_length is None:
                max_length = Config.MAX_RESPONSE_LENGTH
            
            # Format the input prompt
            prompt = f"[PYTHON][QUESTION] {question.strip()} [ANSWER]"
            
            # Tokenize input
            inputs = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=inputs.shape[1] + max_length,
                    num_return_sequences=1,
                    temperature=0.7,
                    top_p=0.9,
                    top_k=50,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    attention_mask=torch.ones_like(inputs)
                )
            
            # Decode response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract only the answer part
            if "[ANSWER]" in response:
                response = response.split("[ANSWER]")[-1].strip()
            
            # Clean up response
            response = self._clean_response(response)
            
            response_time = time.time() - start_time
            logger.info(f"Generated response in {response_time:.2f} seconds")
            
            return response, response_time
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "I apologize, but I encountered an error while processing your question. Please try again.", 0.0
    
    def _clean_response(self, response):
        """Clean and format the generated response"""
        # Remove incomplete sentences at the end
        sentences = response.split('.')
        if len(sentences) > 1 and len(sentences[-1].strip()) < 10:
            response = '.'.join(sentences[:-1]) + '.'
        
        # Fix common formatting issues
        response = response.replace('\n\n\n', '\n\n')
        response = response.replace('  ', ' ')
        
        # Ensure code blocks are properly formatted
        if '```' in response:
            parts = response.split('```')
            for i in range(1, len(parts), 2):  # Every odd index is code
                if not parts[i].startswith('python'):
                    parts[i] = 'python\n' + parts[i]
            response = '```'.join(parts)
        
        return response.strip()
    
    def fine_tune(self, training_data, output_dir="./fine_tuned_model"):
        """Fine-tune the model with new training data"""
        if not ML_AVAILABLE:
            return self.simple_expert.train(training_data)
        
        try:
            logger.info("Starting fine-tuning process")
            
            # Prepare training data
            train_texts = []
            for item in training_data:
                formatted_text = f"[PYTHON][QUESTION] {item['question']} [ANSWER] {item['answer']}"
                train_texts.append(formatted_text)
            
            # Save training data to file
            train_file = os.path.join(output_dir, "train_data.txt")
            os.makedirs(output_dir, exist_ok=True)
            
            with open(train_file, 'w', encoding='utf-8') as f:
                for text in train_texts:
                    f.write(text + '\n')
            
            # Create dataset
            dataset = TextDataset(
                tokenizer=self.tokenizer,
                file_path=train_file,
                block_size=128
            )
            
            # Data collator
            data_collator = DataCollatorForLanguageModeling(
                tokenizer=self.tokenizer,
                mlm=False
            )
            
            # Training arguments
            training_args = TrainingArguments(
                output_dir=output_dir,
                overwrite_output_dir=True,
                num_train_epochs=Config.TRAINING_EPOCHS,
                per_device_train_batch_size=Config.TRAINING_BATCH_SIZE,
                save_steps=500,
                save_total_limit=2,
                prediction_loss_only=True,
                learning_rate=Config.LEARNING_RATE,
                warmup_steps=100,
                logging_steps=100,
                logging_dir=os.path.join(output_dir, "logs"),
            )
            
            # Create trainer
            trainer = Trainer(
                model=self.model,
                args=training_args,
                data_collator=data_collator,
                train_dataset=dataset,
            )
            
            # Train the model
            trainer.train()
            
            # Save the fine-tuned model
            trainer.save_model()
            self.tokenizer.save_pretrained(output_dir)
            
            logger.info(f"Fine-tuning completed. Model saved to {output_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Error during fine-tuning: {str(e)}")
            return False
    
    def evaluate_response_quality(self, question, answer):
        """Evaluate the quality of a response using simple heuristics"""
        score = 0.0
        
        # Length check (not too short, not too long)
        if 50 <= len(answer) <= 2000:
            score += 0.2
        
        # Python-related keywords
        python_keywords = ['python', 'def', 'class', 'import', 'function', 'variable', 'list', 'dict', 'string']
        keyword_count = sum(1 for keyword in python_keywords if keyword.lower() in answer.lower())
        score += min(keyword_count * 0.1, 0.3)
        
        # Code examples
        if '```' in answer or 'def ' in answer or 'import ' in answer:
            score += 0.2
        
        # Coherence (simple check for complete sentences)
        sentences = answer.split('.')
        complete_sentences = [s for s in sentences if len(s.strip()) > 10]
        if len(complete_sentences) >= 2:
            score += 0.2
        
        # Relevance to question
        question_words = set(question.lower().split())
        answer_words = set(answer.lower().split())
        overlap = len(question_words & answer_words)
        score += min(overlap * 0.02, 0.1)
        
        return min(score, 1.0)
    
    def save_model(self, path):
        """Save the current model"""
        if not ML_AVAILABLE:
            logger.info("Simple expert model doesn't require saving")
            return True
        
        try:
            self.model.save_pretrained(path)
            self.tokenizer.save_pretrained(path)
            logger.info(f"Model saved to {path}")
            return True
        except Exception as e:
            logger.error(f"Error saving model: {str(e)}")
            return False
    
    def load_model_from_path(self, path):
        """Load a model from a specific path"""
        if not ML_AVAILABLE:
            logger.info("Simple expert doesn't support loading from path")
            return True
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(path)
            self.model = AutoModelForCausalLM.from_pretrained(path)
            self.model.to(self.device)
            logger.info(f"Model loaded from {path}")
            return True
        except Exception as e:
            logger.error(f"Error loading model from {path}: {str(e)}")
            return False
    
    def get_model_info(self):
        """Get information about the current model"""
        if not ML_AVAILABLE:
            return self.simple_expert.get_model_info()
        
        return {
            'name': self.model_name,
            'device': self.device,
            'cache_dir': self.cache_dir,
            'model_size': self.model.num_parameters() if self.model else 0,
            'type': 'Transformer-based'
        }
