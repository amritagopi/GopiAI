"""
Tests for LLM Adapters
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add paths for imports
core_path = os.path.join(os.path.dirname(__file__), "..", "gopiai")
if core_path not in sys.path:
    sys.path.append(core_path)

class TestBaseAdapter(unittest.TestCase):
    """Test cases for Base Adapter"""
    
    def test_base_adapter_cannot_be_instantiated(self):
        """Test that BaseAdapter cannot be instantiated directly"""
        from gopiai.core.adapters.base_adapter import BaseAdapter
        
        with self.assertRaises(TypeError):
            BaseAdapter()

class TestGeminiAdapter(unittest.TestCase):
    """Test cases for Gemini Adapter"""
    
    @patch('gopiai.core.adapters.gemini_adapter.LITELLM_AVAILABLE', False)
    def test_gemini_adapter_without_litellm(self):
        """Test Gemini adapter initialization without litellm"""
        from gopiai.core.adapters.gemini_adapter import GeminiAdapter
        
        adapter = GeminiAdapter()
        self.assertFalse(adapter.is_available())
        self.assertEqual(adapter.get_provider_name(), "gemini")
    
    @patch('gopiai.core.adapters.gemini_adapter.LITELLM_AVAILABLE', True)
    @patch('os.getenv')
    def test_gemini_adapter_with_api_key(self, mock_getenv):
        """Test Gemini adapter initialization with API key"""
        mock_getenv.return_value = "test-api-key"
        
        from gopiai.core.adapters.gemini_adapter import GeminiAdapter
        
        adapter = GeminiAdapter()
        self.assertTrue(adapter.is_available())
        self.assertEqual(adapter.get_provider_name(), "gemini")
    
    @patch('gopiai.core.adapters.gemini_adapter.LITELLM_AVAILABLE', True)
    @patch('os.getenv')
    def test_gemini_adapter_without_api_key(self, mock_getenv):
        """Test Gemini adapter initialization without API key"""
        mock_getenv.return_value = None
        
        from gopiai.core.adapters.gemini_adapter import GeminiAdapter
        
        adapter = GeminiAdapter()
        self.assertFalse(adapter.is_available())
        self.assertEqual(adapter.get_provider_name(), "gemini")

class TestOpenRouterAdapter(unittest.TestCase):
    """Test cases for OpenRouter Adapter"""
    
    @patch('gopiai.core.adapters.openrouter_adapter.LITELLM_AVAILABLE', False)
    def test_openrouter_adapter_without_litellm(self):
        """Test OpenRouter adapter initialization without litellm"""
        from gopiai.core.adapters.openrouter_adapter import OpenRouterAdapter
        
        adapter = OpenRouterAdapter()
        self.assertFalse(adapter.is_available())
        self.assertEqual(adapter.get_provider_name(), "openrouter")
    
    @patch('gopiai.core.adapters.openrouter_adapter.LITELLM_AVAILABLE', True)
    @patch('os.getenv')
    def test_openrouter_adapter_with_api_key(self, mock_getenv):
        """Test OpenRouter adapter initialization with API key"""
        mock_getenv.return_value = "test-api-key"
        
        from gopiai.core.adapters.openrouter_adapter import OpenRouterAdapter
        
        adapter = OpenRouterAdapter()
        self.assertTrue(adapter.is_available())
        self.assertEqual(adapter.get_provider_name(), "openrouter")
    
    @patch('gopiai.core.adapters.openrouter_adapter.LITELLM_AVAILABLE', True)
    @patch('os.getenv')
    def test_openrouter_adapter_without_api_key(self, mock_getenv):
        """Test OpenRouter adapter initialization without API key"""
        mock_getenv.return_value = None
        
        from gopiai.core.adapters.openrouter_adapter import OpenRouterAdapter
        
        adapter = OpenRouterAdapter()
        self.assertFalse(adapter.is_available())
        self.assertEqual(adapter.get_provider_name(), "openrouter")

if __name__ == '__main__':
    unittest.main()
