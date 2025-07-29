"""
Tests for UI LLM Client with provider switching functionality
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add paths for imports
ui_path = os.path.join(os.path.dirname(__file__), "..", "gopiai")
if ui_path not in sys.path:
    sys.path.append(ui_path)

class TestUiLlmClient(unittest.TestCase):
    """Test cases for UI LLM Client provider switching"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Clear global client instance
        import gopiai.ui.llm
        gopiai.ui.llm._llm_client = None
    
    @patch('gopiai.ui.llm.NEW_LLM_CLIENT_AVAILABLE', False)
    def test_fallback_client_initialization(self):
        """Test that UI client falls back to old implementation when new client is not available"""
        from gopiai.ui.llm import get_llm_client
        
        client = get_llm_client()
        self.assertIsNotNone(client)
        self.assertTrue(hasattr(client, 'call'))
        self.assertTrue(hasattr(client, 'is_available'))
    
    @patch('gopiai.ui.llm.NEW_LLM_CLIENT_AVAILABLE', True)
    @patch('gopiai.ui.llm.LlmClient')
    def test_new_client_initialization(self, mock_llm_client_class):
        """Test that UI client uses new implementation when available"""
        # Mock the LlmClient
        mock_instance = MagicMock()
        mock_llm_client_class.instance.return_value = mock_instance
        
        from gopiai.ui.llm import get_llm_client
        
        client = get_llm_client()
        self.assertIsNotNone(client)
        
        # Verify that the new client was used
        mock_llm_client_class.instance.assert_called_once()
    
    @patch('gopiai.ui.llm.NEW_LLM_CLIENT_AVAILABLE', True)
    @patch('gopiai.ui.llm.LlmClient')
    def test_provider_switching_ui(self, mock_llm_client_class):
        """Test provider switching through UI client"""
        # Mock the LlmClient
        mock_instance = MagicMock()
        mock_instance.swap_provider = MagicMock(return_value=True)
        mock_llm_client_class.instance.return_value = mock_instance
        
        from gopiai.ui.llm import get_llm_client
        
        client = get_llm_client()
        
        # Test switching provider
        import asyncio
        async def test_swap():
            return await client.swap_provider("openrouter")
        
        result = asyncio.run(test_swap())
        self.assertTrue(result)
        mock_instance.swap_provider.assert_called_once_with("openrouter")
    
    def test_client_singleton_pattern(self):
        """Test that UI LLM client follows singleton pattern"""
        from gopiai.ui.llm import get_llm_client
        
        client1 = get_llm_client()
        client2 = get_llm_client()
        
        self.assertIs(client1, client2)

if __name__ == '__main__':
    unittest.main()
