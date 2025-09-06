#!/usr/bin/env python3
"""
Test the improved fixtures to ensure they work correctly.
"""

import pytest


def test_ai_service_mocker(ai_service_mocker):
    """Test the AI service mocker fixture."""
    # Test basic response
    response = ai_service_mocker.get_next_response()
    assert response.content is not None
    assert response.model is not None
    assert response.provider is not None
    
    # Test provider-specific responses
    openai_response = ai_service_mocker.get_provider_response("openai")
    assert "OpenAI" in openai_response.content
    
    anthropic_response = ai_service_mocker.get_provider_response("anthropic")
    assert "Claude" in anthropic_response.content


def test_mock_crewai_server(mock_crewai_server):
    """Test the CrewAI server mock."""
    import requests
    
    # Test health check
    response = requests.get("http://localhost:5051/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    
    # Test models endpoint
    response = requests.get("http://localhost:5051/models")
    assert response.status_code == 200
    models = response.json()
    assert "openai" in models
    assert "anthropic" in models


def test_mock_txtai_memory(mock_txtai_memory):
    """Test the txtai memory mock."""
    # Test search
    results = mock_txtai_memory.search("test query")
    assert len(results) > 0
    assert all("score" in result for result in results)
    
    # Test indexing
    mock_txtai_memory.index(["test document 1", "test document 2"])
    assert mock_txtai_memory.indexed is True
    
    # Test count
    count = mock_txtai_memory.count()
    assert isinstance(count, int)


def test_mock_pyside6_app(mock_pyside6_app):
    """Test the PySide6 app mock."""
    app_data = mock_pyside6_app
    assert "app" in app_data
    assert "message_box" in app_data
    
    # Test message box mocks
    message_box = app_data["message_box"]
    assert "information" in message_box
    assert "warning" in message_box
    assert "critical" in message_box


def test_mock_gopiai_widgets(mock_gopiai_widgets):
    """Test the GopiAI widgets mock."""
    widgets = mock_gopiai_widgets
    
    # Test model selector
    assert widgets["model_selector"].get_current_model() == "gpt-4"
    assert widgets["model_selector"].get_current_provider() == "openai"
    
    # Test chat widget
    assert widgets["chat_widget"].get_message_text() == "Test message"
    
    # Test settings panel
    assert widgets["settings_panel"].get_theme() == "dark"


def test_mock_model_config_manager(mock_model_config_manager):
    """Test the model configuration manager mock."""
    manager = mock_model_config_manager
    
    # Test available models
    models = manager.get_available_models()
    assert "openai" in models
    assert "gpt-4" in models["openai"]
    
    # Test current model
    assert manager.get_current_model() == "gpt-4"
    assert manager.get_current_provider() == "openai"
    
    # Test model switching
    assert manager.switch_model() is True


def test_mock_usage_tracker(mock_usage_tracker):
    """Test the usage tracker mock."""
    tracker = mock_usage_tracker
    
    # Test request checking
    assert tracker.can_make_request() is True
    
    # Test usage stats
    stats = tracker.get_usage_stats()
    assert "requests_made" in stats
    assert "tokens_used" in stats
    assert "requests_remaining" in stats


def test_mock_conversation_manager(mock_conversation_manager):
    """Test the conversation manager mock."""
    manager = mock_conversation_manager
    
    # Test getting conversations
    conversations = manager.get_conversations()
    assert len(conversations) > 0
    assert all("id" in conv for conv in conversations)
    
    # Test creating conversation
    new_id = manager.create_conversation()
    assert new_id == "new_conv_id"
    
    # Test getting specific conversation
    conv = manager.get_conversation()
    assert "id" in conv
    assert "messages" in conv


def test_mock_settings_manager(mock_settings_manager):
    """Test the settings manager mock."""
    manager = mock_settings_manager
    
    # Test getting settings
    theme = manager.get_setting("theme")
    assert theme == "dark"
    
    font_size = manager.get_setting("font_size")
    assert font_size == 12
    
    # Test getting all settings
    all_settings = manager.get_all_settings()
    assert "theme" in all_settings
    assert "font_size" in all_settings


def test_mock_tool_manager(mock_tool_manager):
    """Test the tool manager mock."""
    manager = mock_tool_manager
    
    # Test available tools
    tools = manager.get_available_tools()
    assert "browser_tools" in tools
    assert "filesystem_tools" in tools
    
    # Test tool availability
    assert manager.is_tool_available("browser_tools") is True
    assert manager.is_tool_available("terminal_tools") is False
    
    # Test tool execution
    result = manager.execute_tool()
    assert result["status"] == "success"


def test_sample_conversation(sample_conversation):
    """Test the sample conversation fixture."""
    conv = sample_conversation
    
    assert conv.id is not None
    assert len(conv.messages) > 0
    assert conv.metadata is not None
    
    # Check message structure
    for message in conv.messages:
        assert "role" in message
        assert "content" in message


def test_mock_database(mock_database):
    """Test the mock database fixture."""
    db = mock_database
    
    # Test connection
    assert db.connected is True
    
    # Test data operations
    users = db.select("users")
    assert len(users) > 0
    
    conversations = db.select("conversations")
    assert len(conversations) > 0
    
    # Test insertion
    new_id = db.insert("test_table", {"name": "test"})
    assert new_id is not None
    
    # Test selection with filters
    filtered = db.select("users", {"name": "Test User"})
    assert len(filtered) > 0


@pytest.mark.integration
def test_fixtures_integration(ai_service_mocker, mock_crewai_server, mock_txtai_memory):
    """Test that fixtures work together."""
    # This test ensures that multiple fixtures can be used together
    # without conflicts
    
    # Test AI service
    response = ai_service_mocker.get_next_response()
    assert response is not None
    
    # Test server mock
    import requests
    server_response = requests.get("http://localhost:5051/health")
    assert server_response.status_code == 200
    
    # Test memory
    memory_results = mock_txtai_memory.search("integration test")
    assert len(memory_results) > 0
    
    # All fixtures should work together without issues
    assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])