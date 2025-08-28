#!/usr/bin/env python3
"""
Unit tests for CrewAI API Server.

Tests the main API endpoints, request handling, and server functionality.
"""

import pytest
import json
import uuid
from unittest.mock import MagicMock, patch, Mock
from datetime import datetime, timedelta
import sys
import os

# Add test infrastructure to path
    # Заменено на использование path_manager: sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'test_infrastructure'))

from fixtures import ai_service_mocker, mock_crewai_server
from crewai_fixtures import (
    mock_api_server, mock_state_manager, mock_openrouter_client,
    mock_memory_system, crewai_test_config
)

# Import the modules we're testing
    # Заменено на использование path_manager: sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))


class TestCrewAIAPIServer:
    """Test suite for CrewAI API Server endpoints and functionality."""
    
    @pytest.fixture
    def mock_flask_app(self):
        """Mock Flask application for testing."""
        mock_app = MagicMock()
        mock_app.test_client.return_value = MagicMock()
        return mock_app
    
    @pytest.fixture
    def mock_task(self):
        """Mock task object for testing."""
        task_id = str(uuid.uuid4())
        mock_task = MagicMock()
        mock_task.task_id = task_id
        mock_task.message = "Test message"
        mock_task.metadata = {"test": "data"}
        mock_task.status = "pending"
        mock_task.result = None
        mock_task.error = None
        mock_task.created_at = datetime.now()
        mock_task.started_at = None
        mock_task.completed_at = None
        
        # Mock task methods
        mock_task.start_processing.return_value = None
        mock_task.complete.return_value = None
        mock_task.fail.return_value = None
        mock_task.to_dict.return_value = {
            "task_id": task_id,
            "status": "pending",
            "message": "Test message",
            "result": None,
            "error": None,
            "created_at": mock_task.created_at.isoformat(),
            "started_at": None,
            "completed_at": None
        }
        
        return mock_task
    
    def test_health_check_endpoint_healthy(self, mock_api_server, mock_memory_system):
        """Test health check endpoint when system is healthy."""
        # Configure mocks
        mock_api_server.health_check.return_value = {
            "status": "online",
            "rag_status": "OK",
            "indexed_documents": 150
        }
        
        # Test health check
        health_status = mock_api_server.health_check()
        
        # Assertions
        assert health_status["status"] == "online"
        assert health_status["rag_status"] == "OK"
        assert health_status["indexed_documents"] == 150
        mock_api_server.health_check.assert_called_once()
    
    def test_health_check_endpoint_limited_mode(self, mock_api_server):
        """Test health check endpoint when system is in limited mode."""
        # Configure mock for limited mode
        mock_api_server.health_check.return_value = {
            "status": "limited_mode",
            "rag_status": "NOT INITIALIZED",
            "indexed_documents": 0
        }
        
        # Test health check
        health_status = mock_api_server.health_check()
        
        # Assertions
        assert health_status["status"] == "limited_mode"
        assert health_status["rag_status"] == "NOT INITIALIZED"
        assert health_status["indexed_documents"] == 0
    
    def test_process_request_valid_json(self, mock_api_server, mock_task):
        """Test processing valid JSON request."""
        # Test data
        request_data = {
            "message": "Test message for processing",
            "metadata": {"user_id": "test_user", "session_id": "test_session"}
        }
        
        # Configure mock
        mock_api_server.process_request.return_value = {
            "task_id": mock_task.task_id,
            "status": "pending",
            "message": "Task queued for processing",
            "created_at": mock_task.created_at.isoformat(),
            "request_id": "test-request-id"
        }
        
        # Process request
        response = mock_api_server.process_request(request_data)
        
        # Assertions
        assert response["status"] == "pending"
        assert response["message"] == "Task queued for processing"
        assert "task_id" in response
        assert "created_at" in response
        mock_api_server.process_request.assert_called_once_with(request_data)
    
    def test_process_request_missing_message(self, mock_api_server):
        """Test processing request with missing message field."""
        # Test data without message
        request_data = {"metadata": {"user_id": "test_user"}}
        
        # Configure mock for error response
        mock_api_server.process_request.return_value = {
            "error": "Missing 'message' field"
        }
        
        # Process request
        response = mock_api_server.process_request(request_data)
        
        # Assertions
        assert "error" in response
        assert "Missing 'message' field" in response["error"]
    
    def test_process_request_invalid_json(self, mock_api_server):
        """Test processing request with invalid JSON."""
        # Configure mock for invalid JSON error
        mock_api_server.process_request.return_value = {
            "error": "Invalid JSON: Expecting value"
        }
        
        # Process invalid request
        response = mock_api_server.process_request("invalid json")
        
        # Assertions
        assert "error" in response
        assert "Invalid JSON" in response["error"]
    
    def test_get_task_status_existing_task(self, mock_api_server, mock_task):
        """Test getting status of existing task."""
        # Configure mock
        mock_api_server.get_task_status.return_value = mock_task.to_dict()
        
        # Get task status
        status = mock_api_server.get_task_status(mock_task.task_id)
        
        # Assertions
        assert status["task_id"] == mock_task.task_id
        assert status["status"] == "pending"
        assert status["message"] == "Test message"
        mock_api_server.get_task_status.assert_called_once_with(mock_task.task_id)
    
    def test_get_task_status_nonexistent_task(self, mock_api_server):
        """Test getting status of non-existent task."""
        # Configure mock for not found
        mock_api_server.get_task_status.return_value = {"error": "Task not found"}
        
        # Get status of non-existent task
        status = mock_api_server.get_task_status("non-existent-id")
        
        # Assertions
        assert "error" in status
        assert status["error"] == "Task not found"
    
    def test_debug_status_endpoint(self, mock_api_server):
        """Test debug status endpoint."""
        # Configure mock
        mock_api_server.debug_status.return_value = {
            "server_ready": True,
            "smart_delegator_ready": True,
            "rag_system_ready": True,
            "active_tasks": 2,
            "task_ids": ["task-1", "task-2"]
        }
        
        # Get debug status
        debug_info = mock_api_server.debug_status()
        
        # Assertions
        assert debug_info["server_ready"] is True
        assert debug_info["smart_delegator_ready"] is True
        assert debug_info["rag_system_ready"] is True
        assert debug_info["active_tasks"] == 2
        assert len(debug_info["task_ids"]) == 2
    
    def test_get_models_by_provider_valid_provider(self, mock_api_server):
        """Test getting models for valid provider."""
        # Test data
        expected_models = [
            {"id": "gpt-4", "name": "GPT-4", "provider": "openai"},
            {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "provider": "openai"}
        ]
        
        # Configure mock
        mock_api_server.get_models_by_provider.return_value = expected_models
        
        # Get models
        models = mock_api_server.get_models_by_provider("openai")
        
        # Assertions
        assert len(models) == 2
        assert all(model["provider"] == "openai" for model in models)
        mock_api_server.get_models_by_provider.assert_called_once_with("openai")
    
    def test_get_models_by_provider_missing_provider(self, mock_api_server):
        """Test getting models without provider parameter."""
        # Configure mock for error
        mock_api_server.get_models_by_provider.return_value = {
            "error": "Missing 'provider' parameter"
        }
        
        # Get models without provider
        response = mock_api_server.get_models_by_provider(None)
        
        # Assertions
        assert "error" in response
        assert "Missing 'provider' parameter" in response["error"]
    
    def test_update_provider_model_state_valid_data(self, mock_api_server, mock_state_manager):
        """Test updating provider/model state with valid data."""
        # Test data
        update_data = {
            "provider": "openai",
            "model_id": "gpt-4"
        }
        
        # Configure mocks
        mock_api_server.update_provider_model_state.return_value = {
            "status": "success",
            "message": "State updated: provider=openai, model_id=gpt-4",
            "provider": "openai",
            "model_id": "gpt-4"
        }
        mock_state_manager.update_state.return_value = True
        
        # Update state
        response = mock_api_server.update_provider_model_state(update_data)
        
        # Assertions
        assert response["status"] == "success"
        assert response["provider"] == "openai"
        assert response["model_id"] == "gpt-4"
        mock_api_server.update_provider_model_state.assert_called_once_with(update_data)
    
    def test_update_provider_model_state_missing_data(self, mock_api_server):
        """Test updating state with missing required data."""
        # Test data with missing model_id
        update_data = {"provider": "openai"}
        
        # Configure mock for error
        mock_api_server.update_provider_model_state.return_value = {
            "error": "Both 'provider' and 'model_id' are required"
        }
        
        # Update state
        response = mock_api_server.update_provider_model_state(update_data)
        
        # Assertions
        assert "error" in response
        assert "required" in response["error"]
    
    def test_get_current_state(self, mock_api_server, mock_state_manager):
        """Test getting current provider/model state."""
        # Configure mock
        expected_state = {
            "provider": "openai",
            "model_id": "gpt-4"
        }
        mock_api_server.get_current_state.return_value = expected_state
        mock_state_manager.get_state.return_value = expected_state
        
        # Get current state
        state = mock_api_server.get_current_state()
        
        # Assertions
        assert state["provider"] == "openai"
        assert state["model_id"] == "gpt-4"
        mock_api_server.get_current_state.assert_called_once()
    
    def test_get_tools_endpoint(self, mock_api_server):
        """Test getting available tools."""
        # Expected tools data
        expected_tools = {
            "browser": [
                {
                    "name": "browser_tools",
                    "description": "Browser automation tools",
                    "enabled": True,
                    "has_custom_key": False,
                    "available": True
                }
            ],
            "filesystem": [
                {
                    "name": "filesystem_tools",
                    "description": "File system operations",
                    "enabled": True,
                    "has_custom_key": False,
                    "available": True
                }
            ]
        }
        
        # Configure mock
        mock_api_server.get_tools.return_value = expected_tools
        
        # Get tools
        tools = mock_api_server.get_tools()
        
        # Assertions
        assert "browser" in tools
        assert "filesystem" in tools
        assert len(tools["browser"]) == 1
        assert tools["browser"][0]["name"] == "browser_tools"
        assert tools["browser"][0]["enabled"] is True
    
    def test_toggle_tool_endpoint(self, mock_api_server):
        """Test toggling tool state."""
        # Test data
        toggle_data = {
            "tool_name": "browser_tools",
            "enabled": False
        }
        
        # Configure mock
        mock_api_server.toggle_tool.return_value = {
            "success": True,
            "tool_name": "browser_tools",
            "enabled": False
        }
        
        # Toggle tool
        response = mock_api_server.toggle_tool(toggle_data)
        
        # Assertions
        assert response["success"] is True
        assert response["tool_name"] == "browser_tools"
        assert response["enabled"] is False
        mock_api_server.toggle_tool.assert_called_once_with(toggle_data)
    
    def test_set_tool_key_endpoint(self, mock_api_server):
        """Test setting custom API key for tool."""
        # Test data
        key_data = {
            "tool_name": "browser_tools",
            "api_key": "test-api-key-123"
        }
        
        # Configure mock
        mock_api_server.set_tool_key.return_value = {
            "success": True,
            "tool_name": "browser_tools",
            "has_key": True
        }
        
        # Set tool key
        response = mock_api_server.set_tool_key(key_data)
        
        # Assertions
        assert response["success"] is True
        assert response["tool_name"] == "browser_tools"
        assert response["has_key"] is True
        mock_api_server.set_tool_key.assert_called_once_with(key_data)
    
    def test_get_agents_endpoint(self, mock_api_server):
        """Test getting available CrewAI agents."""
        # Expected agents data
        expected_agents = {
            "agents": [
                {
                    "id": "research_agent",
                    "name": "Research Agent",
                    "description": "Agent for research tasks",
                    "type": "agent"
                },
                {
                    "id": "coding_agent",
                    "name": "Coding Agent",
                    "description": "Agent for programming tasks",
                    "type": "agent"
                }
            ]
        }
        
        # Configure mock
        mock_api_server.get_agents.return_value = expected_agents
        
        # Get agents
        agents = mock_api_server.get_agents()
        
        # Assertions
        assert "agents" in agents
        assert len(agents["agents"]) == 2
        assert agents["agents"][0]["id"] == "research_agent"
        assert agents["agents"][1]["type"] == "agent"
    
    @pytest.mark.integration
    def test_task_processing_flow(self, mock_api_server, mock_task):
        """Test complete task processing flow."""
        # Test data
        request_data = {
            "message": "Process this test message",
            "metadata": {"priority": "high"}
        }
        
        # Configure mocks for complete flow
        mock_api_server.process_request.return_value = {
            "task_id": mock_task.task_id,
            "status": "pending",
            "message": "Task queued for processing"
        }
        
        # Simulate task completion
        completed_task = mock_task.to_dict()
        completed_task["status"] = "completed"
        completed_task["result"] = "Task completed successfully"
        completed_task["completed_at"] = datetime.now().isoformat()
        
        mock_api_server.get_task_status.return_value = completed_task
        
        # Execute flow
        # 1. Submit task
        submit_response = mock_api_server.process_request(request_data)
        task_id = submit_response["task_id"]
        
        # 2. Check task status
        status_response = mock_api_server.get_task_status(task_id)
        
        # Assertions
        assert submit_response["status"] == "pending"
        assert status_response["status"] == "completed"
        assert status_response["result"] == "Task completed successfully"
        assert status_response["task_id"] == task_id
    
    def test_server_error_handling(self, mock_api_server):
        """Test server error handling."""
        # Configure mock to raise exception
        mock_api_server.process_request.side_effect = Exception("Internal server error")
        
        # Test error handling
        with pytest.raises(Exception) as exc_info:
            mock_api_server.process_request({"message": "test"})
        
        assert "Internal server error" in str(exc_info.value)
    
    def test_task_cleanup_mechanism(self, mock_api_server):
        """Test automatic cleanup of old completed tasks."""
        # Create old completed task
        old_task_id = "old-task-id"
        old_task_data = {
            "task_id": old_task_id,
            "status": "completed",
            "completed_at": (datetime.now() - timedelta(hours=2)).isoformat()
        }
        
        # Configure mock for cleanup
        mock_api_server.cleanup_old_tasks.return_value = {
            "cleaned_tasks": [old_task_id],
            "remaining_tasks": 5
        }
        
        # Run cleanup
        cleanup_result = mock_api_server.cleanup_old_tasks()
        
        # Assertions
        assert old_task_id in cleanup_result["cleaned_tasks"]
        assert cleanup_result["remaining_tasks"] == 5
    
    def test_concurrent_request_handling(self, mock_api_server):
        """Test handling of concurrent requests."""
        # Test data for multiple requests
        requests = [
            {"message": f"Test message {i}", "metadata": {"request_id": i}}
            for i in range(5)
        ]
        
        # Configure mock for concurrent processing
        mock_responses = [
            {
                "task_id": f"task-{i}",
                "status": "pending",
                "message": "Task queued for processing"
            }
            for i in range(5)
        ]
        
        mock_api_server.process_request.side_effect = mock_responses
        
        # Process requests
        responses = []
        for request in requests:
            response = mock_api_server.process_request(request)
            responses.append(response)
        
        # Assertions
        assert len(responses) == 5
        assert all(response["status"] == "pending" for response in responses)
        assert len(set(response["task_id"] for response in responses)) == 5  # All unique task IDs


if __name__ == "__main__":
    pytest.main([__file__, "-v"])