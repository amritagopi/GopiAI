"""
Base Adapter for LLM providers
Defines the common interface for all LLM adapters
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Union

class BaseAdapter(ABC):
    """Abstract base class for LLM adapters"""
    
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate a response from the LLM
        
        Args:
            prompt: The prompt to generate a response for
            **kwargs: Additional arguments for the generation
            
        Returns:
            The generated response
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the adapter is available (API key present, service accessible)
        
        Returns:
            True if the adapter is available, False otherwise
        """
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Get the name of the provider this adapter supports
        
        Returns:
            The provider name
        """
        pass
