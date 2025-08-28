"""
Model Manager for GopiAI
Handles model configuration and switching between different LLM providers
"""

import os
import json
import logging
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict, field
from pathlib import Path

logger = logging.getLogger(__name__)

class ModelProvider(Enum):
    """Supported model providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    COHERE = "cohere"
    OPENROUTER = "openrouter"
    GEMINI = "gemini"

@dataclass
class ModelConfiguration:
    """Configuration for a language model"""
    provider: ModelProvider
    model_id: str
    display_name: str
    api_key_env: str
    is_active: bool = True
    is_default: bool = False
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        data = asdict(self)
        data['provider'] = self.provider.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ModelConfiguration':
        """Create configuration from dictionary"""
        data = data.copy()
        data['provider'] = ModelProvider(data['provider'])
        return cls(**data)
    
    def is_available(self) -> bool:
        """Check if configuration is available (API key exists)"""
        api_key = os.getenv(self.api_key_env)
        return api_key is not None and api_key.strip() != ""

class ModelManager:
    """Manager for model configurations"""
    
    CONFIG_FILE = "model_configs.json"
    
    def __init__(self, config_dir: Optional[str] = None):
        """Initialize the model manager"""
        if config_dir is None:
            config_dir = os.path.join(os.path.expanduser("~"), ".config", "gopiai")
        
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / self.CONFIG_FILE
        
        self._configurations: Dict[str, ModelConfiguration] = {}
        self._current_model_id: Optional[str] = None
        
        self._load_configurations()
        self._ensure_default_configurations()
        
        logger.info(f"ModelManager initialized with {len(self._configurations)} configurations")
    
    def _load_configurations(self):
        """Load configurations from file"""
        if not self.config_file.exists():
            logger.info(f"No configuration file found at {self.config_file}")
            return
            
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            self._configurations = {
                config_id: ModelConfiguration.from_dict(config_data)
                for config_id, config_data in data.get('configurations', {}).items()
            }
            self._current_model_id = data.get('current_model_id')
            
            logger.info(f"Loaded {len(self._configurations)} model configurations")
            
        except Exception as e:
            logger.error(f"Error loading model configurations: {e}")
            self._configurations = {}
    
    def _save_configurations(self):
        """Save configurations to file"""
        try:
            data = {
                'configurations': {
                    config_id: config.to_dict()
                    for config_id, config in self._configurations.items()
                },
                'current_model_id': self._current_model_id
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Error saving model configurations: {e}")
    
    def _ensure_default_configurations(self):
        """Ensure default configurations exist"""
        default_configs = [
            # OpenAI models
            ModelConfiguration(
                provider=ModelProvider.OPENAI,
                model_id="gpt-4-turbo-preview",
                display_name="GPT-4 Turbo",
                api_key_env="OPENAI_API_KEY",
                is_default=True,
                parameters={"temperature": 0.7, "max_tokens": 2000}
            ),
            ModelConfiguration(
                provider=ModelProvider.OPENAI,
                model_id="gpt-3.5-turbo",
                display_name="GPT-3.5 Turbo",
                api_key_env="OPENAI_API_KEY",
                parameters={"temperature": 0.7, "max_tokens": 1000}
            ),
            
            # Anthropic models
            ModelConfiguration(
                provider=ModelProvider.ANTHROPIC,
                model_id="claude-3-opus-20240229",
                display_name="Claude 3 Opus",
                api_key_env="ANTHROPIC_API_KEY"
            ),
            
            # Gemini models (via Google AI Studio)
            ModelConfiguration(
                provider=ModelProvider.GEMINI,
                model_id="gemini-pro",
                display_name="Gemini Pro",
                api_key_env="GOOGLE_API_KEY"
            ),
        ]
        
        # Add default configs if they don't exist
        config_updated = False
        for config in default_configs:
            if config.model_id not in self._configurations:
                self._configurations[config.model_id] = config
                config_updated = True
                
                # Set first model with is_default=True as current if not set
                if config.is_default and self._current_model_id is None:
                    self._current_model_id = config.model_id
        
        # If no default was set, use the first available model
        if not self._current_model_id and self._configurations:
            self._current_model_id = next(iter(self._configurations.keys()))
        
        if config_updated:
            self._save_configurations()
    
    def get_available_models(self) -> List[ModelConfiguration]:
        """Get list of available model configurations"""
        return [
            config for config in self._configurations.values()
            if config.is_available()
        ]
    
    def get_current_model(self) -> Optional[ModelConfiguration]:
        """Get current model configuration"""
        if self._current_model_id and self._current_model_id in self._configurations:
            return self._configurations[self._current_model_id]
        return None
    
    def set_current_model(self, model_id: str) -> bool:
        """Set current model by ID"""
        if model_id in self._configurations:
            self._current_model_id = model_id
            self._save_configurations()
            logger.info(f"Current model set to: {model_id}")
            return True
        return False
    
    def add_model(self, config: ModelConfiguration) -> bool:
        """Add a new model configuration"""
        self._configurations[config.model_id] = config
        self._save_configurations()
        logger.info(f"Added model: {config.model_id}")
        return True
    
    def remove_model(self, model_id: str) -> bool:
        """Remove a model configuration"""
        if model_id in self._configurations:
            del self._configurations[model_id]
            
            # Reset current model if it was removed
            if self._current_model_id == model_id:
                self._current_model_id = next(iter(self._configurations.keys()), None)
                
            self._save_configurations()
            logger.info(f"Removed model: {model_id}")
            return True
        return False

# Global instance
_model_manager = None

def get_model_manager() -> ModelManager:
    """Get the global model manager instance"""
    global _model_manager
    if _model_manager is None:
        _model_manager = ModelManager()
    return _model_manager
