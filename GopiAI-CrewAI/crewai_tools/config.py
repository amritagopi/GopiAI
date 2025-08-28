"""
Configuration settings for CrewAI Tools
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional

# Base configuration
BASE_CONFIG = {
    # Model configurations
    "models": {
        "default_provider": "openai",
        "providers": {
            "openai": {
                "api_key_env": "OPENAI_API_KEY",
                "default_model": "gpt-4-turbo-preview",
                "models": {
                    "gpt-4-turbo-preview": {
                        "display_name": "GPT-4 Turbo",
                        "parameters": {
                            "temperature": 0.7,
                            "max_tokens": 2000
                        }
                    },
                    "gpt-3.5-turbo": {
                        "display_name": "GPT-3.5 Turbo",
                        "parameters": {
                            "temperature": 0.7,
                            "max_tokens": 1000
                        }
                    }
                }
            },
            "anthropic": {
                "api_key_env": "ANTHROPIC_API_KEY",
                "default_model": "claude-3-opus-20240229",
                "models": {
                    "claude-3-opus-20240229": {
                        "display_name": "Claude 3 Opus",
                        "parameters": {
                            "temperature": 0.7,
                            "max_tokens": 4000
                        }
                    },
                    "claude-3-sonnet-20240229": {
                        "display_name": "Claude 3 Sonnet",
                        "parameters": {
                            "temperature": 0.7,
                            "max_tokens": 4000
                        }
                    }
                }
            },
            "gemini": {
                "api_key_env": "GOOGLE_API_KEY",
                "default_model": "gemini-pro",
                "models": {
                    "gemini-pro": {
                        "display_name": "Gemini Pro",
                        "parameters": {
                            "temperature": 0.7,
                            "max_tokens": 2000
                        }
                    }
                }
            }
        }
    },
    
    # Tool configurations
    "tools": {
        "web_search": {
            "enabled": True,
            "provider": "serper",  # or "google", "serpapi"
            "api_key_env": "SERPER_API_KEY"
        },
        "file_system": {
            "enabled": True,
            "allowed_directories": [
                str(Path.home() / "Documents"),
                str(Path.cwd())
            ]
        }
    },
    
    # Logging configuration
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "file": None  # Set to a path to enable file logging
    }
}

def get_config() -> Dict[str, Any]:
    """
    Get the current configuration.
    
    Returns:
        Dict[str, Any]: The current configuration
    """
    return BASE_CONFIG

def get_model_config(provider: str, model_id: str) -> Optional[Dict[str, Any]]:
    """
    Get configuration for a specific model.
    
    Args:
        provider: The provider name (e.g., 'openai', 'anthropic')
        model_id: The model ID (e.g., 'gpt-4-turbo')
        
    Returns:
        Optional[Dict[str, Any]]: The model configuration, or None if not found
    """
    config = get_config()
    providers = config.get('models', {}).get('providers', {})
    
    if provider not in providers:
        return None
        
    models = providers[provider].get('models', {})
    return models.get(model_id)
