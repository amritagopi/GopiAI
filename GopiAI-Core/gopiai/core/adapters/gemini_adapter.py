"""
Gemini Adapter for LLM Client
Implements the BaseAdapter interface for Google Gemini models
"""

import os
import asyncio
import logging
from typing import Optional, Dict, Any
from .base_adapter import BaseAdapter

# Try to import litellm for Gemini support
try:
    import litellm
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False
    print("Warning: litellm not available, Gemini adapter will not work")

logger = logging.getLogger(__name__)

class GeminiAdapter(BaseAdapter):
    """Adapter for Google Gemini models"""
    
    def __init__(self):
        self.provider_name = "gemini"
        self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        
        if not self.api_key:
            logger.warning("No Gemini API key found in environment variables")
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate a response using Google Gemini
        
        Args:
            prompt: The prompt to generate a response for
            **kwargs: Additional arguments for the generation
            
        Returns:
            The generated response
        """
        if not LITELLM_AVAILABLE:
            raise RuntimeError("litellm is not available")
        
        if not self.is_available():
            raise RuntimeError("Gemini adapter is not available (no API key)")
        
        try:
            # Prepare messages
            messages = kwargs.get("messages", [{"role": "user", "content": prompt}])
            if not messages:
                messages = [{"role": "user", "content": prompt}]
            
            # Set default parameters
            temperature = kwargs.get("temperature", 0.7)
            max_tokens = kwargs.get("max_tokens", 2048)
            model = kwargs.get("model", "gemini/gemini-1.5-flash")
            
            # Ensure model name is correct
            if not model.startswith("gemini/"):
                model = f"gemini/{model}"
            
            # Add timeout handling
            timeout = kwargs.get("timeout", 120)  # Default 120 seconds
            
            # Call Gemini through litellm
            response = await asyncio.wait_for(
                self._call_litellm(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                ),
                timeout=timeout
            )
            
            if response and response.choices and len(response.choices) > 0:
                return response.choices[0].message.content or ""
            else:
                raise RuntimeError("Empty response from Gemini")
                
        except asyncio.TimeoutError:
            logger.error("Timeout while calling Gemini API")
            raise RuntimeError("Timeout while calling Gemini API")
        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}")
            raise
    
    async def _call_litellm(self, model: str, messages: list, temperature: float, max_tokens: int):
        """Internal method to call litellm with proper error handling"""
        return await litellm.acompletion(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            api_key=self.api_key
        )
    
    def is_available(self) -> bool:
        """
        Check if the Gemini adapter is available
        
        Returns:
            True if the adapter is available, False otherwise
        """
        return LITELLM_AVAILABLE and bool(self.api_key)
    
    def get_provider_name(self) -> str:
        """
        Get the name of the provider this adapter supports
        
        Returns:
            The provider name
        """
        return self.provider_name
