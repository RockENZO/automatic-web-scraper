"""
Smart Model Manager for Ollama
Automatically handles model selection and fallback for memory constraints.
"""

import logging
from langchain_ollama import OllamaLLM
import subprocess
import time

logger = logging.getLogger(__name__)

class SmartModelManager:
    """Manages model selection with automatic fallback for memory issues."""
    
    def __init__(self):
        self.models = [
            {
                "name": "gpt-oss:20b",
                "memory_req": "12GB",
                "performance": "highest",
                "config": {
                    "temperature": 0.1,
                    "num_predict": 500,
                    "num_ctx": 2048,
                    "repeat_penalty": 1.1,
                    "top_k": 20,
                    "top_p": 0.9,
                }
            },
            {
                "name": "llama3.1:8b",
                "memory_req": "6GB", 
                "performance": "high",
                "config": {
                    "temperature": 0.1,
                    "num_predict": 800,
                    "num_ctx": 4096,
                }
            },
            {
                "name": "llama3.1",
                "memory_req": "6GB",
                "performance": "high", 
                "config": {
                    "temperature": 0.1,
                    "num_predict": 800,
                    "num_ctx": 4096,
                }
            },
            {
                "name": "phi3:mini",
                "memory_req": "2GB",
                "performance": "medium",
                "config": {
                    "temperature": 0.2,
                    "num_predict": 600,
                    "num_ctx": 2048,
                }
            }
        ]
        self.current_model_index = 0
        self.failed_models = set()
    
    def get_available_models(self):
        """Get list of available models from Ollama."""
        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                available = []
                for line in lines:
                    if line.strip():
                        model_name = line.split()[0]
                        available.append(model_name)
                return available
            return []
        except Exception as e:
            logger.error(f"Error getting available models: {e}")
            return []
    
    def is_model_available(self, model_name):
        """Check if a specific model is available."""
        available = self.get_available_models()
        return any(model_name in avail for avail in available)
    
    def get_current_model(self):
        """Get the current model configuration."""
        while self.current_model_index < len(self.models):
            model = self.models[self.current_model_index]
            
            # Skip failed models
            if model["name"] in self.failed_models:
                self.current_model_index += 1
                continue
                
            # Check if model is available
            if self.is_model_available(model["name"]):
                return model
            else:
                logger.warning(f"Model {model['name']} not available, trying next...")
                self.current_model_index += 1
                continue
        
        return None
    
    def create_model_instance(self, model_config=None):
        """Create an Ollama model instance with the current or specified config."""
        if model_config is None:
            model_config = self.get_current_model()
        
        if model_config is None:
            raise Exception("No suitable models available")
        
        logger.info(f"Creating model instance: {model_config['name']} (Memory req: {model_config['memory_req']})")
        
        try:
            return OllamaLLM(
                model=model_config["name"],
                **model_config["config"]
            )
        except Exception as e:
            logger.error(f"Failed to create model {model_config['name']}: {e}")
            raise
    
    def handle_model_failure(self, error_message):
        """Handle model failure and switch to next available model."""
        current_model = self.get_current_model()
        if current_model:
            model_name = current_model["name"]
            self.failed_models.add(model_name)
            logger.error(f"Model {model_name} failed: {error_message}")
            logger.info(f"Adding {model_name} to failed models list")
        
        self.current_model_index += 1
        next_model = self.get_current_model()
        
        if next_model:
            logger.info(f"Switching to fallback model: {next_model['name']}")
            return self.create_model_instance(next_model)
        else:
            logger.error("No more fallback models available")
            return None
    
    def install_fallback_models(self):
        """Install common fallback models."""
        fallback_models = ["llama3.1:8b", "phi3:mini"]
        
        for model_name in fallback_models:
            if not self.is_model_available(model_name):
                logger.info(f"Installing fallback model: {model_name}")
                try:
                    result = subprocess.run(['ollama', 'pull', model_name], 
                                          capture_output=True, text=True, timeout=300)
                    if result.returncode == 0:
                        logger.info(f"Successfully installed {model_name}")
                    else:
                        logger.error(f"Failed to install {model_name}: {result.stderr}")
                except subprocess.TimeoutExpired:
                    logger.warning(f"Timeout installing {model_name}")
                except Exception as e:
                    logger.error(f"Error installing {model_name}: {e}")
    
    def get_model_recommendations(self):
        """Get memory optimization recommendations."""
        recommendations = []
        
        # Check available memory (rough estimation)
        try:
            result = subprocess.run(['vm_stat'], capture_output=True, text=True)
            if result.returncode == 0:
                # Parse memory info (basic estimation)
                recommendations.append("💡 Memory Optimization Tips:")
                recommendations.append("   • Close other memory-intensive applications")
                recommendations.append("   • Use smaller chunk sizes (2000-4000 characters)")
                recommendations.append("   • Process fewer chunks at once")
                recommendations.append("   • Consider using llama3.1:8b for better memory efficiency")
        except:
            pass
        
        return recommendations

# Global instance
model_manager = SmartModelManager()
