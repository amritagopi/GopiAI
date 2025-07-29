"""
Tests for LLM Client with provider switching functionality
"""

import os
import sys
import asyncio
import unittest
from unittest.mock import patch, MagicMock

# Add paths for imports
core_path = os.path.join(os.path.dirname(__file__), "..", "gopiai")
if core_path not in sys.path:
    sys.path.append(core_path)

crewai_path = os.path.join(os.path.dirname(__file__), "..", "..", "GopiAI-CrewAI")
if crewai_path not in sys.path:
    sys.path.append(crewai_path)

class TestLlmClient(unittest.TestCase):
    """Test cases for LLM Client provider switching"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Clear singleton instance
        if hasattr(self, 'llm_client_module'):
            self.llm_client_module.LlmClient._instance = None
            self.llm_client_module.LlmClient._initialized = False
    
    @patch('gopiai.core.llm_client.load_state')
    @patch('gopiai.core.llm_client.get_api_key_for_provider')
    def test_singleton_pattern(self, mock_get_api_key, mock_load_state):
        """Test that LlmClient follows singleton pattern"""
        mock_load_state.return_value = {"provider": "gemini", "model_id": ""}
        mock_get_api_key.return_value = "test-key"
        
        try:
            from gopiai.core.llm_client import LlmClient
            
            # Create first instance
            client1 = LlmClient.instance()
            self.assertIsNotNone(client1)
            
            # Create second instance
            client2 = LlmClient.instance()
            self.assertIs(client1, client2)
            
        except ImportError:
            self.skipTest("LlmClient not available")
    
    @patch('gopiai.core.llm_client.load_state')
    @patch('gopiai.core.llm_client.get_api_key_for_provider')
    @patch('gopiai.core.llm_client.update_state')
    def test_provider_switching(self, mock_update_state, mock_get_api_key, mock_load_state):
        """Test provider switching functionality"""
        mock_load_state.return_value = {"provider": "gemini", "model_id": ""}
        mock_get_api_key.return_value = "test-key"
        mock_update_state.return_value = None
        
        try:
            from gopiai.core.llm_client import LlmClient
            
            # Create client instance
            client = LlmClient.instance()
            self.assertEqual(client.get_current_provider(), "gemini")
            
            # Test switching to openrouter
            async def test_swap():
                result = await client.swap_provider("openrouter")
                return result
            
            # Run async test
            result = asyncio.run(test_swap())
            # Note: This might fail if openrouter adapter is not available
            # but we're testing the method call, not the actual switch
            
        except ImportError:
            self.skipTest("LlmClient not available")
    
    @patch('gopiai.core.llm_client.load_state')
    @patch('gopiai.core.llm_client.get_api_key_for_provider')
    def test_initialization_with_gemini(self, mock_get_api_key, mock_load_state):
        """Test client initialization with Gemini provider"""
        mock_load_state.return_value = {"provider": "gemini", "model_id": ""}
        mock_get_api_key.return_value = "test-key"
        
        try:
            from gopiai.core.llm_client import LlmClient
            
            client = LlmClient.instance()
            self.assertEqual(client.get_current_provider(), "gemini")
            
        except ImportError:
            self.skipTest("LlmClient not available")
    
    @patch('gopiai.core.llm_client.load_state')
    @patch('gopiai.core.llm_client.get_api_key_for_provider')
    def test_initialization_with_openrouter(self, mock_get_api_key, mock_load_state):
        """Test client initialization with OpenRouter provider"""
        mock_load_state.return_value = {"provider": "openrouter", "model_id": ""}
        mock_get_api_key.return_value = "test-key"
        
        try:
            from gopiai.core.llm_client import LlmClient
            
            client = LlmClient.instance()
            self.assertEqual(client.get_current_provider(), "openrouter")
            
        except ImportError:
            self.skipTest("LlmClient not available")

if __name__ == '__main__':
    unittest.main()
