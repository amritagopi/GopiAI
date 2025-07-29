"""
Enhanced LLM Client for GopiAI Core
Supports proper provider switching with singleton pattern and reinitialization
"""

import os
import sys
import logging
from typing import Optional, Dict, Any
from pathlib import Path

# Добавляем путь к CrewAI модулям для доступа к llm_rotation_config
crewai_path = Path(__file__).parent.parent.parent.parent / "GopiAI-CrewAI"
if str(crewai_path) not in sys.path:
    sys.path.append(str(crewai_path))

try:
    from llm_rotation_config import (
        select_llm_model_safe, 
        get_api_key_for_provider,
        PROVIDER_KEY_ENV,
        update_state,
        get_current_provider
    )
    from state_manager import load_state, save_state
except ImportError as e:
    print(f"Warning: Could not import llm_rotation_config: {e}")

logger = logging.getLogger(__name__)

class LlmClient:
    """Enhanced LLM Client with proper provider switching support"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LlmClient, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._provider = None
            self._adapter = None
            self._current_model = None
            self._initialize_client()
            LlmClient._initialized = True
            logger.info("LlmClient initialized")
    
    def _initialize_client(self):
        """Initialize the client with current provider from state"""
        try:
            # Load current state
            state = load_state()
            self._provider = state.get("provider", "gemini")
            self._current_model = state.get("model_id", "")
            
            # Load the appropriate adapter
            self._load_adapter(self._provider)
            
            logger.info(f"LlmClient initialized with provider: {self._provider}")
        except Exception as e:
            logger.error(f"Error initializing LlmClient: {e}")
            # Fallback to default provider
            self._provider = "gemini"
            self._load_adapter("gemini")
    
    def _load_adapter(self, provider: str):
        """Load the appropriate adapter for the given provider"""
        try:
            if provider == "gemini":
                from .adapters.gemini_adapter import GeminiAdapter
                self._adapter = GeminiAdapter()
            elif provider == "openrouter":
                from .adapters.openrouter_adapter import OpenRouterAdapter
                self._adapter = OpenRouterAdapter()
            else:
                raise ValueError(f"Unsupported provider: {provider}")
            
            logger.info(f"Loaded adapter for provider: {provider}")
        except Exception as e:
            logger.error(f"Error loading adapter for {provider}: {e}")
            # Fallback to Gemini adapter
            from .adapters.gemini_adapter import GeminiAdapter
            self._adapter = GeminiAdapter()
            self._provider = "gemini"
    
    async def swap_provider(self, new_provider: str) -> bool:
        """
        Swap the current provider and reinitialize the adapter
        
        Args:
            new_provider: The new provider to switch to
            
        Returns:
            True if the switch was successful, False otherwise
        """
        if new_provider == self._provider:
            logger.info(f"Provider already set to {new_provider}")
            return True
        
        if new_provider not in PROVIDER_KEY_ENV:
            logger.error(f"Unsupported provider: {new_provider}")
            return False
        
        # Check if API key is available
        api_key = get_api_key_for_provider(new_provider)
        if not api_key:
            logger.warning(f"No API key found for provider: {new_provider}")
            # We'll still try to switch, but it might fail later
        
        try:
            # Update state
            update_state(new_provider, "")  # Model will be selected later
            
            # Load new adapter
            self._load_adapter(new_provider)
            self._provider = new_provider
            self._current_model = None
            
            logger.info(f"Successfully switched to provider: {new_provider}")
            return True
        except Exception as e:
            logger.error(f"Error switching to provider {new_provider}: {e}")
            return False
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate a response using the current provider
        
        Args:
            prompt: The prompt to generate a response for
            **kwargs: Additional arguments for the generation
            
        Returns:
            The generated response
        """
        if self._adapter is None:
            raise RuntimeError("LLM adapter not initialized")
        
        try:
            # Select appropriate model if not already selected
            if not self._current_model:
                task_type = kwargs.get("task_type", "dialog")
                model = select_llm_model_safe(task_type)
                if model:
                    self._current_model = model["id"]
                    logger.info(f"Selected model: {self._current_model}")
            
            # Generate response
            response = await self._adapter.generate(prompt, **kwargs)
            return response
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise
    
    def get_current_provider(self) -> str:
        """Get the current provider"""
        return self._provider
    
    def get_current_model(self) -> Optional[str]:
        """Get the current model"""
        return self._current_model
    
    @classmethod
    def instance(cls) -> 'LlmClient':
        """Get the singleton instance of LlmClient"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @classmethod
    async def reinitialize(cls) -> 'LlmClient':
        """
        Reinitialize the singleton instance
        This should be called when configuration changes
        """
        if cls._instance is not None:
            cls._instance._initialized = False
            cls._instance.__init__()
        else:
            cls._instance = cls()
        return cls._instance

# Backward compatibility
get_llm_client = LlmClient.instance
