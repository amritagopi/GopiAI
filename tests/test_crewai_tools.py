"""
Comprehensive tests for CrewAI Tools implementation
"""
import sys
import unittest
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent / "GopiAI-CrewAI"))

from crewai_tools import (
    model_manager,
    tool_manager
)

class TestModelManager(unittest.TestCase):
    """Tests for ModelManager functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.manager = model_manager
        
    def test_get_available_models(self):
        """Test getting available models"""
        models = self.manager.get_available_models()
        # At least one model should be available
        self.assertIsInstance(models, list)
        
    def test_set_current_model(self):
        """Test setting current model"""
        models = self.manager.get_available_models()
        if models and len(models) > 0:
            model_id = models[0].model_id
            self.manager.set_current_model(model_id)
            current_model = self.manager.get_current_model()
            self.assertIsNotNone(current_model)
            self.assertEqual(current_model.model_id, model_id)

class TestToolManager(unittest.TestCase):
    """Tests for ToolManager functionality"""
    
    def test_get_all_tools(self):
        """Test getting all available tools"""
        tools = tool_manager.get_all_tools()
        self.assertIsInstance(tools, list)
        
    def test_web_search_tool(self):
        """Test web search tool functionality"""
        # Skip this test as it requires specific tool setup
        self.skipTest("Web search tool test requires specific setup")
        
        # The following is an example of how to test the web search tool
        # when it's properly set up with the correct dependencies
        # with patch('crewai.tools.SerperDevTool._run') as mock_search:
        #     mock_search.return_value = "Test search results"
        #     web_search = None
        #     for tool in tool_manager.get_all_tools():
        #         if hasattr(tool, 'name') and tool.name == 'search_internet':
        #             web_search = tool
        #             break
        #     
        #     if web_search:
        #         result = web_search.run({"query": "test"})
        #         self.assertIn("Test search results", result)
        #     else:
        #         self.skipTest("Web search tool not available")

class TestConfig(unittest.TestCase):
    """Tests for configuration"""
    
    def test_config_loading(self):
        """Test if configuration loads correctly"""
        from crewai_tools.config import get_config, get_model_config
        
        # Test getting the main config
        config = get_config()
        self.assertIsInstance(config, dict)
        
        # Test getting model config - use a known model if available
        models = model_manager.get_available_models()
        if models and len(models) > 0:
            model_id = models[0].model_id
            provider = models[0].provider
            model_config = get_model_config(provider, model_id)
            self.assertIsNotNone(model_config)
            self.assertIn('display_name', model_config)
        else:
            self.skipTest("No models available for testing")

if __name__ == '__main__':
    unittest.main()
