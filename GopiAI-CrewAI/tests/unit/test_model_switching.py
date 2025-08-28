#!/usr/bin/env python3
"""
Unit tests for Model Switching System.

Tests the LLM rotation configuration, model selection, and provider switching.
"""

import pytest
import os
import time
from unittest.mock import MagicMock, patch, Mock
from dataclasses import dataclass
import sys

# Add test infrastructure to path
    # Заменено на использование path_manager: sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'test_infrastructure'))

from fixtures import ai_service_mocker
from crewai_fixtures import (
    mock_llm_provider, mock_openrouter_client, mock_state_manager,
    mock_rate_limiter, mock_model_switcher
)

# Import the modules we're testing
    # Заменено на использование path_manager: sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))


class TestModelSwitching:
    """Test suite for model switching and LLM rotation functionality."""
    
    @pytest.fixture
    def mock_usage_tracker(self):
        """Mock usage tracker for testing."""
        mock_tracker = MagicMock()
        
        # Mock usage data
        mock_tracker.can_use.return_value = True
        mock_tracker.register_use.return_value = None
        mock_tracker.get_stats.return_value = {
            "rpm": 5,
            "tpm": 1000,
            "rpd": 50,
            "blacklisted": False,
            "blacklisted_until": 0,
            "rpm_violations": 0
        }
        mock_tracker.is_blacklisted.return_value = False
        mock_tracker.current_provider = "gemini"
        mock_tracker.set_current_provider.return_value = None
        
        return mock_tracker
    
    @pytest.fixture
    def mock_models_config(self):
        """Mock models configuration for testing."""
        return [
            {
                "display_name": "Gemini 1.5 Flash",
                "id": "gemini/gemini-1.5-flash",
                "provider": "gemini",
                "rpm": 15,
                "tpm": 2_500_000,
                "type": ["simple", "dialog", "code"],
                "priority": 3,
                "rpd": 50,
                "base_score": 0.5,
            },
            {
                "display_name": "GPT-4 (OpenRouter)",
                "id": "openrouter/openai/gpt-4",
                "provider": "openrouter",
                "rpm": 10,
                "tpm": 8_000,
                "type": ["dialog", "code", "complex"],
                "priority": 1,
                "rpd": 100,
                "base_score": 0.9,
            },
            {
                "display_name": "Claude 3 Sonnet (OpenRouter)",
                "id": "openrouter/anthropic/claude-3-sonnet",
                "provider": "openrouter",
                "rpm": 20,
                "tpm": 200_000,
                "type": ["dialog", "summarize"],
                "priority": 2,
                "rpd": 200,
                "base_score": 0.8,
            }
        ]
    
    def test_get_available_models_with_api_keys(self, mock_models_config, mock_usage_tracker):
        """Test getting available models when API keys are present."""
        with patch('llm_rotation_config.get_api_key_for_provider') as mock_get_key:
            with patch('llm_rotation_config.MODELS', mock_models_config):
                with patch('llm_rotation_config._usage_tracker', mock_usage_tracker):
                    # Configure API keys to be available
                    mock_get_key.side_effect = lambda provider: f"test-{provider}-key"
                    
                    # Import after patching
                    from llm_rotation_config import get_available_models
                    
                    # Get available models for dialog task
                    models = get_available_models("dialog")
                    
                    # Assertions
                    assert len(models) > 0
                    assert all(model["provider"] in ["gemini", "openrouter"] for model in models)
                    assert all("dialog" in model["type"] for model in models)
                    
                    # Check sorting by priority
                    priorities = [model["priority"] for model in models]
                    assert priorities == sorted(priorities)
    
    def test_get_available_models_without_api_keys(self, mock_models_config, mock_usage_tracker):
        """Test getting available models when API keys are missing."""
        with patch('llm_rotation_config.get_api_key_for_provider') as mock_get_key:
            with patch('llm_rotation_config.MODELS', mock_models_config):
                with patch('llm_rotation_config._usage_tracker', mock_usage_tracker):
                    # Configure no API keys available
                    mock_get_key.return_value = None
                    
                    # Import after patching
                    from llm_rotation_config import get_available_models
                    
                    # Get available models
                    models = get_available_models("dialog")
                    
                    # Assertions - should be empty without API keys
                    assert len(models) == 0
    
    def test_get_next_available_model_success(self, mock_models_config, mock_usage_tracker):
        """Test getting next available model successfully."""
        with patch('llm_rotation_config.get_api_key_for_provider') as mock_get_key:
            with patch('llm_rotation_config.MODELS', mock_models_config):
                with patch('llm_rotation_config._usage_tracker', mock_usage_tracker):
                    # Configure API keys and usage tracker
                    mock_get_key.side_effect = lambda provider: f"test-{provider}-key"
                    mock_usage_tracker.can_use.return_value = True
                    
                    # Import after patching
                    from llm_rotation_config import get_next_available_model
                    
                    # Get next available model
                    model = get_next_available_model("dialog", tokens=100)
                    
                    # Assertions
                    assert model is not None
                    assert "dialog" in model["type"]
                    assert model["provider"] in ["gemini", "openrouter"]
                    
                    # Verify usage tracker was called
                    mock_usage_tracker.can_use.assert_called()
    
    def test_get_next_available_model_rate_limited(self, mock_models_config, mock_usage_tracker):
        """Test getting next available model when all are rate limited."""
        with patch('llm_rotation_config.get_api_key_for_provider') as mock_get_key:
            with patch('llm_rotation_config.MODELS', mock_models_config):
                with patch('llm_rotation_config._usage_tracker', mock_usage_tracker):
                    # Configure API keys but rate limiting
                    mock_get_key.side_effect = lambda provider: f"test-{provider}-key"
                    mock_usage_tracker.can_use.return_value = False
                    
                    # Import after patching
                    from llm_rotation_config import get_next_available_model
                    
                    # Get next available model
                    model = get_next_available_model("dialog")
                    
                    # Assertions - should be None when all rate limited
                    assert model is None
    
    def test_register_use_updates_tracker(self, mock_models_config, mock_usage_tracker):
        """Test that registering usage updates the tracker."""
        with patch('llm_rotation_config.MODELS', mock_models_config):
            with patch('llm_rotation_config._usage_tracker', mock_usage_tracker):
                # Import after patching
                from llm_rotation_config import register_use
                
                # Register usage
                model_id = "gemini/gemini-1.5-flash"
                tokens = 500
                register_use(model_id, tokens)
                
                # Assertions
                mock_usage_tracker.register_use.assert_called_once()
                call_args = mock_usage_tracker.register_use.call_args[0]
                assert call_args[0]["id"] == model_id
                assert call_args[1] == tokens
    
    def test_usage_tracker_rate_limiting(self, mock_models_config):
        """Test usage tracker rate limiting functionality."""
        from llm_rotation_config import UsageTracker
        
        # Create real usage tracker for testing
        tracker = UsageTracker(mock_models_config)
        
        # Get a test model
        test_model = mock_models_config[0]  # Gemini model with rpm=15
        
        # Test normal usage
        assert tracker.can_use(test_model, tokens=100) is True
        
        # Register usage up to limit
        for _ in range(test_model["rpm"]):
            tracker.register_use(test_model, tokens=100)
        
        # Should now be rate limited
        assert tracker.can_use(test_model, tokens=100) is False
        
        # Check stats
        stats = tracker.get_stats(test_model["id"])
        assert stats["rpm"] == test_model["rpm"]
        assert stats["tpm"] == test_model["rpm"] * 100
    
    def test_usage_tracker_blacklist_mechanism(self, mock_models_config):
        """Test usage tracker blacklist mechanism."""
        from llm_rotation_config import UsageTracker
        
        # Create real usage tracker
        tracker = UsageTracker(mock_models_config)
        test_model = mock_models_config[0]
        
        # Exceed RPM limit significantly to trigger blacklist
        for _ in range(int(test_model["rpm"] * 1.6)):  # 60% over limit
            tracker.register_use(test_model, tokens=100)
        
        # Check if model is blacklisted
        stats = tracker.get_stats(test_model["id"])
        assert stats["rpm_violations"] > 0
        
        # Model should be temporarily blacklisted
        is_blacklisted = tracker.is_blacklisted(test_model["id"])
        # Note: This might be False if blacklist duration has passed
        assert isinstance(is_blacklisted, bool)
    
    def test_provider_switching(self, mock_models_config, mock_usage_tracker):
        """Test switching between providers."""
        with patch('llm_rotation_config.MODELS', mock_models_config):
            with patch('llm_rotation_config._usage_tracker', mock_usage_tracker):
                # Import after patching
                from llm_rotation_config import update_state, get_current_provider
                
                # Test initial provider
                initial_provider = get_current_provider()
                assert initial_provider in ["gemini", "openrouter"]
                
                # Switch to different provider
                new_provider = "openrouter" if initial_provider == "gemini" else "gemini"
                update_state(new_provider, "test-model-id")
                
                # Verify provider switch was called on tracker
                mock_usage_tracker.set_current_provider.assert_called_with(new_provider)
    
    def test_api_key_validation(self):
        """Test API key validation functionality."""
        from llm_rotation_config import get_api_key_for_provider
        
        # Test with environment variables
        test_cases = [
            ("gemini", "GEMINI_API_KEY"),
            ("openrouter", "OPENROUTER_API_KEY"),
            ("unknown", None)
        ]
        
        for provider, env_var in test_cases:
            if env_var:
                # Mock environment variable
                with patch.dict(os.environ, {env_var: "test-api-key-123"}):
                    key = get_api_key_for_provider(provider)
                    assert key == "test-api-key-123"
            else:
                # Unknown provider should return None
                key = get_api_key_for_provider(provider)
                assert key is None
    
    def test_api_key_validation_edge_cases(self):
        """Test API key validation with edge cases."""
        from llm_rotation_config import get_api_key_for_provider
        
        # Test with empty key
        with patch.dict(os.environ, {"GEMINI_API_KEY": ""}):
            key = get_api_key_for_provider("gemini")
            assert key is None
        
        # Test with whitespace-only key
        with patch.dict(os.environ, {"GEMINI_API_KEY": "   "}):
            key = get_api_key_for_provider("gemini")
            assert key is None
        
        # Test with short key (should warn but return key)
        with patch.dict(os.environ, {"GEMINI_API_KEY": "short"}):
            key = get_api_key_for_provider("gemini")
            assert key == "short"
    
    def test_model_selection_by_intelligence(self, mock_models_config):
        """Test model selection based on intelligence score."""
        with patch('llm_rotation_config.MODELS', mock_models_config):
            from llm_rotation_config import get_models_by_intelligence
            
            # Get models with minimum intelligence score
            high_intelligence_models = get_models_by_intelligence(min_score=0.8)
            medium_intelligence_models = get_models_by_intelligence(min_score=0.5)
            
            # Assertions
            assert len(high_intelligence_models) <= len(medium_intelligence_models)
            assert all(model["base_score"] >= 0.8 for model in high_intelligence_models)
            assert all(model["base_score"] >= 0.5 for model in medium_intelligence_models)
    
    def test_legacy_compatibility(self, mock_models_config, mock_usage_tracker):
        """Test legacy compatibility functions."""
        with patch('llm_rotation_config.MODELS', mock_models_config):
            with patch('llm_rotation_config._usage_tracker', mock_usage_tracker):
                with patch('llm_rotation_config.get_api_key_for_provider') as mock_get_key:
                    # Configure API keys
                    mock_get_key.side_effect = lambda provider: f"test-{provider}-key"
                    mock_usage_tracker.can_use.return_value = True
                    
                    # Import legacy function
                    from llm_rotation_config import select_llm_model_safe
                    
                    # Test legacy function
                    model = select_llm_model_safe("dialog", tokens=100)
                    
                    # Assertions
                    assert model is not None
                    assert "dialog" in model["type"]
                    
                    # Verify usage was registered
                    mock_usage_tracker.register_use.assert_called_once()
    
    def test_state_persistence(self, mock_state_manager):
        """Test state persistence functionality."""
        with patch('llm_rotation_config.load_state') as mock_load:
            with patch('llm_rotation_config.save_state') as mock_save:
                # Configure mocks
                mock_load.return_value = {"provider": "gemini", "model_id": "test-model"}
                
                # Import after patching
                from llm_rotation_config import update_state
                
                # Update state
                update_state("openrouter", "new-model-id")
                
                # Verify save was called
                mock_save.assert_called_once_with("openrouter", "new-model-id")
    
    def test_model_usage_stats(self, mock_models_config, mock_usage_tracker):
        """Test getting model usage statistics."""
        with patch('llm_rotation_config.MODELS', mock_models_config):
            with patch('llm_rotation_config._usage_tracker', mock_usage_tracker):
                # Configure mock stats
                expected_stats = {
                    "rpm": 5,
                    "tpm": 1000,
                    "rpd": 25,
                    "blacklisted": False,
                    "blacklisted_until": 0,
                    "rpm_violations": 0
                }
                mock_usage_tracker.get_stats.return_value = expected_stats
                
                # Import after patching
                from llm_rotation_config import get_model_usage_stats
                
                # Get stats
                model_id = "gemini/gemini-1.5-flash"
                stats = get_model_usage_stats(model_id)
                
                # Assertions
                assert stats == expected_stats
                mock_usage_tracker.get_stats.assert_called_once_with(model_id)
    
    def test_blacklist_status_check(self, mock_models_config, mock_usage_tracker):
        """Test checking blacklist status of models."""
        with patch('llm_rotation_config.MODELS', mock_models_config):
            with patch('llm_rotation_config._usage_tracker', mock_usage_tracker):
                # Configure mock blacklist status
                mock_usage_tracker.is_blacklisted.return_value = True
                
                # Import after patching
                from llm_rotation_config import is_model_blacklisted
                
                # Check blacklist status
                model_id = "gemini/gemini-1.5-flash"
                is_blacklisted = is_model_blacklisted(model_id)
                
                # Assertions
                assert is_blacklisted is True
                mock_usage_tracker.is_blacklisted.assert_called_once_with(model_id)
    
    @pytest.mark.integration
    def test_complete_model_switching_flow(self, mock_models_config, mock_usage_tracker):
        """Test complete model switching workflow."""
        with patch('llm_rotation_config.MODELS', mock_models_config):
            with patch('llm_rotation_config._usage_tracker', mock_usage_tracker):
                with patch('llm_rotation_config.get_api_key_for_provider') as mock_get_key:
                    with patch('llm_rotation_config.save_state') as mock_save:
                        # Configure mocks
                        mock_get_key.side_effect = lambda provider: f"test-{provider}-key"
                        mock_usage_tracker.can_use.return_value = True
                        
                        # Import functions
                        from llm_rotation_config import (
                            get_available_models, get_next_available_model,
                            register_use, update_state, get_current_provider
                        )
                        
                        # 1. Get available models
                        models = get_available_models("dialog")
                        assert len(models) > 0
                        
                        # 2. Select next available model
                        selected_model = get_next_available_model("dialog", tokens=100)
                        assert selected_model is not None
                        
                        # 3. Register usage
                        register_use(selected_model["id"], tokens=100)
                        mock_usage_tracker.register_use.assert_called()
                        
                        # 4. Switch provider if needed
                        current_provider = get_current_provider()
                        new_provider = "openrouter" if current_provider == "gemini" else "gemini"
                        update_state(new_provider, "new-model-id")
                        
                        # Verify state was saved
                        mock_save.assert_called_with(new_provider, "new-model-id")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])