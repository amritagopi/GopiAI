#!/usr/bin/env python3
"""
Unit tests for State Manager.

Tests state persistence, loading, and management functionality.
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open
import sys

# Add test infrastructure to path
    # Заменено на использование path_manager: sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'test_infrastructure'))

from fixtures import temp_dir
from crewai_fixtures import mock_state_manager

# Import the modules we're testing
    # Заменено на использование path_manager: sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))


class TestStateManager:
    """Test suite for state management functionality."""
    
    @pytest.fixture
    def mock_state_file(self, temp_dir):
        """Create a mock state file for testing."""
        state_data = {
            "provider": "gemini",
            "model_id": "gemini-1.5-flash"
        }
        
        state_file = temp_dir / "test_state.json"
        with open(state_file, 'w') as f:
            json.dump(state_data, f)
        
        return state_file
    
    @pytest.fixture
    def empty_state_file(self, temp_dir):
        """Create an empty state file for testing."""
        state_file = temp_dir / "empty_state.json"
        state_file.touch()
        return state_file
    
    @pytest.fixture
    def corrupted_state_file(self, temp_dir):
        """Create a corrupted state file for testing."""
        state_file = temp_dir / "corrupted_state.json"
        with open(state_file, 'w') as f:
            f.write("invalid json content {")
        return state_file
    
    def test_load_state_existing_file(self, mock_state_file):
        """Test loading state from existing file."""
        with patch('state_manager.STATE_PATH', mock_state_file):
            from state_manager import load_state
            
            # Load state
            state = load_state()
            
            # Assertions
            assert state["provider"] == "gemini"
            assert state["model_id"] == "gemini-1.5-flash"
    
    def test_load_state_nonexistent_file(self, temp_dir):
        """Test loading state when file doesn't exist."""
        nonexistent_file = temp_dir / "nonexistent.json"
        
        with patch('state_manager.STATE_PATH', nonexistent_file):
            with patch('pathlib.Path.home', return_value=temp_dir / "fake_home"):
                from state_manager import load_state
                
                # Load state
                state = load_state()
                
                # Should return default state
                assert state["provider"] == "gemini"
                assert state["model_id"] == ""
    
    def test_load_state_corrupted_file(self, corrupted_state_file):
        """Test loading state from corrupted file."""
        with patch('state_manager.STATE_PATH', corrupted_state_file):
            from state_manager import load_state
            
            # Load state - should handle corruption gracefully
            state = load_state()
            
            # Should return default state when file is corrupted
            assert state["provider"] == "gemini"
            assert state["model_id"] == ""
    
    def test_load_state_empty_file(self, empty_state_file):
        """Test loading state from empty file."""
        with patch('state_manager.STATE_PATH', empty_state_file):
            from state_manager import load_state
            
            # Load state
            state = load_state()
            
            # Should return default state for empty file
            assert state["provider"] == "gemini"
            assert state["model_id"] == ""
    
    def test_save_state_new_file(self, temp_dir):
        """Test saving state to new file."""
        new_state_file = temp_dir / "new_state.json"
        
        with patch('state_manager.STATE_PATH', new_state_file):
            from state_manager import save_state
            
            # Save state
            save_state("openrouter", "gpt-4")
            
            # Verify file was created and contains correct data
            assert new_state_file.exists()
            with open(new_state_file, 'r') as f:
                saved_data = json.load(f)
            
            assert saved_data["provider"] == "openrouter"
            assert saved_data["model_id"] == "gpt-4"
    
    def test_save_state_existing_file(self, mock_state_file):
        """Test saving state to existing file (overwrite)."""
        with patch('state_manager.STATE_PATH', mock_state_file):
            from state_manager import save_state
            
            # Save new state
            save_state("openrouter", "claude-3-sonnet")
            
            # Verify file was updated
            with open(mock_state_file, 'r') as f:
                saved_data = json.load(f)
            
            assert saved_data["provider"] == "openrouter"
            assert saved_data["model_id"] == "claude-3-sonnet"
    
    def test_save_state_directory_creation(self, temp_dir):
        """Test that save_state creates parent directories if needed."""
        nested_state_file = temp_dir / "nested" / "dir" / "state.json"
        
        with patch('state_manager.STATE_PATH', nested_state_file):
            from state_manager import save_state
            
            # Save state - should create directories
            save_state("gemini", "gemini-2.0-flash")
            
            # Verify directories were created and file exists
            assert nested_state_file.exists()
            assert nested_state_file.parent.exists()
            
            # Verify content
            with open(nested_state_file, 'r') as f:
                saved_data = json.load(f)
            
            assert saved_data["provider"] == "gemini"
            assert saved_data["model_id"] == "gemini-2.0-flash"
    
    def test_save_state_permission_error(self, temp_dir):
        """Test handling of permission errors during save."""
        readonly_file = temp_dir / "readonly_state.json"
        readonly_file.touch()
        readonly_file.chmod(0o444)  # Read-only
        
        with patch('state_manager.STATE_PATH', readonly_file):
            from state_manager import save_state
            
            # Save state - should handle permission error gracefully
            # This should not raise an exception
            save_state("openrouter", "gpt-4")
            
            # File should remain unchanged due to permission error
            # (The actual implementation logs the error but doesn't raise)
    
    def test_get_state_path(self, temp_dir):
        """Test getting the state file path."""
        test_path = temp_dir / "test_state.json"
        
        with patch('state_manager.STATE_PATH', test_path):
            from state_manager import get_state_path
            
            # Get path
            path = get_state_path()
            
            # Assertions
            assert path == test_path
            assert isinstance(path, Path)
    
    def test_legacy_state_migration(self, temp_dir):
        """Test migration from legacy state file location."""
        # Create legacy state file
        legacy_state_data = {
            "provider": "openrouter",
            "model_id": "legacy-model"
        }
        
        legacy_file = temp_dir / ".gopiai_state.json"
        with open(legacy_file, 'w') as f:
            json.dump(legacy_state_data, f)
        
        # New state file location
        new_state_file = temp_dir / ".gopiai" / "state.json"
        
        with patch('state_manager.STATE_PATH', new_state_file):
            with patch('pathlib.Path.home', return_value=temp_dir):
                from state_manager import load_state
                
                # Load state - should migrate from legacy location
                state = load_state()
                
                # Verify migration occurred
                assert state["provider"] == "openrouter"
                assert state["model_id"] == "legacy-model"
                
                # Verify new file was created
                assert new_state_file.exists()
                
                # Verify content in new location
                with open(new_state_file, 'r') as f:
                    migrated_data = json.load(f)
                
                assert migrated_data == legacy_state_data
    
    def test_state_validation(self, temp_dir):
        """Test validation of state data structure."""
        # Create state file with missing required keys
        invalid_state_data = {
            "provider": "gemini"
            # Missing "model_id" key
        }
        
        invalid_state_file = temp_dir / "invalid_state.json"
        with open(invalid_state_file, 'w') as f:
            json.dump(invalid_state_data, f)
        
        with patch('state_manager.STATE_PATH', invalid_state_file):
            from state_manager import load_state
            
            # Load state - should handle invalid structure
            state = load_state()
            
            # Should return default state for invalid structure
            assert state["provider"] == "gemini"
            assert state["model_id"] == ""
    
    def test_state_with_extra_fields(self, temp_dir):
        """Test handling of state files with extra fields."""
        # Create state file with extra fields
        extended_state_data = {
            "provider": "openrouter",
            "model_id": "gpt-4",
            "extra_field": "extra_value",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        extended_state_file = temp_dir / "extended_state.json"
        with open(extended_state_file, 'w') as f:
            json.dump(extended_state_data, f)
        
        with patch('state_manager.STATE_PATH', extended_state_file):
            from state_manager import load_state
            
            # Load state
            state = load_state()
            
            # Should load required fields correctly
            assert state["provider"] == "openrouter"
            assert state["model_id"] == "gpt-4"
            # Extra fields might be preserved depending on implementation
    
    def test_concurrent_state_access(self, temp_dir):
        """Test concurrent access to state file."""
        state_file = temp_dir / "concurrent_state.json"
        
        with patch('state_manager.STATE_PATH', state_file):
            from state_manager import load_state, save_state
            
            # Simulate concurrent operations
            # Save initial state
            save_state("gemini", "initial-model")
            
            # Load state
            state1 = load_state()
            
            # Save different state
            save_state("openrouter", "concurrent-model")
            
            # Load state again
            state2 = load_state()
            
            # Assertions
            assert state1["provider"] == "gemini"
            assert state1["model_id"] == "initial-model"
            assert state2["provider"] == "openrouter"
            assert state2["model_id"] == "concurrent-model"
    
    def test_state_encoding_handling(self, temp_dir):
        """Test handling of different text encodings in state files."""
        # Create state with unicode characters
        unicode_state_data = {
            "provider": "gemini",
            "model_id": "модель-с-кириллицей"
        }
        
        unicode_state_file = temp_dir / "unicode_state.json"
        with open(unicode_state_file, 'w', encoding='utf-8') as f:
            json.dump(unicode_state_data, f, ensure_ascii=False)
        
        with patch('state_manager.STATE_PATH', unicode_state_file):
            from state_manager import load_state, save_state
            
            # Load state with unicode
            state = load_state()
            
            # Verify unicode handling
            assert state["provider"] == "gemini"
            assert state["model_id"] == "модель-с-кириллицей"
            
            # Save state with unicode
            save_state("openrouter", "новая-модель")
            
            # Reload and verify
            updated_state = load_state()
            assert updated_state["model_id"] == "новая-модель"
    
    @pytest.mark.integration
    def test_complete_state_lifecycle(self, temp_dir):
        """Test complete state management lifecycle."""
        state_file = temp_dir / "lifecycle_state.json"
        
        with patch('state_manager.STATE_PATH', state_file):
            with patch('pathlib.Path.home', return_value=temp_dir / "fake_home"):
                from state_manager import load_state, save_state, get_state_path
                
                # 1. Initial load (file doesn't exist)
                initial_state = load_state()
                assert initial_state["provider"] == "gemini"
                assert initial_state["model_id"] == ""
            
            # 2. Save first state
            save_state("openrouter", "gpt-4")
            
            # 3. Load saved state
            loaded_state = load_state()
            assert loaded_state["provider"] == "openrouter"
            assert loaded_state["model_id"] == "gpt-4"
            
            # 4. Update state
            save_state("gemini", "gemini-2.0-flash")
            
            # 5. Load updated state
            updated_state = load_state()
            assert updated_state["provider"] == "gemini"
            assert updated_state["model_id"] == "gemini-2.0-flash"
            
            # 6. Verify file path
            path = get_state_path()
            assert path == state_file
            assert path.exists()
            
            # 7. Verify file content directly
            with open(state_file, 'r') as f:
                file_content = json.load(f)
            
            assert file_content["provider"] == "gemini"
            assert file_content["model_id"] == "gemini-2.0-flash"
    
    def test_state_manager_with_mock(self, mock_state_manager):
        """Test state manager using mock fixture."""
        # Test getting state
        state = mock_state_manager.get_state()
        assert "current_provider" in state
        assert "current_model" in state
        
        # Test updating state
        result = mock_state_manager.update_state("openrouter", "gpt-4")
        assert result is True
        
        # Test saving state
        save_result = mock_state_manager.save_state()
        assert save_result is True
        
        # Test loading state
        loaded_state = mock_state_manager.load_state()
        assert loaded_state is not None
        
        # Test resetting state
        reset_result = mock_state_manager.reset_state()
        assert reset_result is True
        
        # Verify mock was called
        mock_state_manager.get_state.assert_called()
        mock_state_manager.update_state.assert_called_with("openrouter", "gpt-4")
        mock_state_manager.save_state.assert_called()
        mock_state_manager.load_state.assert_called()
        mock_state_manager.reset_state.assert_called()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])