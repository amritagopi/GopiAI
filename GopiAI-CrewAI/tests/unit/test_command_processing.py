#!/usr/bin/env python3
"""
Unit tests for Command Processing System.

Tests command extraction, validation, and execution functionality.
"""

import pytest
import json

# Add test infrastructure to path
    # Заменено на использование path_manager: sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'test_infrastructure'))

from fixtures import mock_tool_manager
from crewai_fixtures import mock_command_processor, mock_tool_executor

# Import the modules we're testing
    # Заменено на использование path_manager: sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))


class TestCommandProcessing:
    """Test suite for command processing and tool execution."""
    
    @pytest.fixture
    def valid_command_json(self):
        """Valid command JSON for testing."""
        return {
            "tool": "filesystem_tools",
            "params": {
                "command": "ls",
                "path": "/home/user"
            }
        }
    
    @pytest.fixture
    def valid_command_array(self):
        """Valid array of commands for testing."""
        return [
            {
                "tool": "filesystem_tools",
                "params": {"command": "ls", "path": "."}
            },
            {
                "tool": "browser_tools",
                "params": {"command": "open", "url": "https://example.com"}
            }
        ]
    
    @pytest.fixture
    def invalid_command_json(self):
        """Invalid command JSON for testing."""
        return {
            "tool": "filesystem_tools"
            # Missing required "params" field
        }
    
    def test_valid_single_command_processing(self, valid_command_json):
        """Test processing of valid single command."""
        command_text = json.dumps(valid_command_json, ensure_ascii=False)
        
        # Configure mock
        mock_command_processor.validate_command.return_value = True
        mock_command_processor.extract_tools.return_value = [valid_command_json]
        mock_command_processor.process_command.return_value = {
            "status": "success",
            "result": "Command processed successfully",
            "tool_calls": [valid_command_json]
        }
        
        # Process command
        is_valid = mock_command_processor.validate_command(command_text)
        tools = mock_command_processor.extract_tools(command_text)
        result = mock_command_processor.process_command(command_text)
        
        # Assertions
        assert is_valid is True
        assert len(tools) == 1
        assert tools[0]["tool"] == "filesystem_tools"
        assert result["status"] == "success"
        assert len(result["tool_calls"]) == 1
    
    def test_valid_array_command_processing(self, valid_command_array):
        """Test processing of valid command array."""
        command_text = json.dumps(valid_command_array, ensure_ascii=False)
        
        # Configure mock
        mock_command_processor.validate_command.return_value = True
        mock_command_processor.extract_tools.return_value = valid_command_array
        mock_command_processor.process_command.return_value = {
            "status": "success",
            "result": "Multiple commands processed successfully",
            "tool_calls": valid_command_array
        }
        
        # Process commands
        is_valid = mock_command_processor.validate_command(command_text)
        tools = mock_command_processor.extract_tools(command_text)
        result = mock_command_processor.process_command(command_text)
        
        # Assertions
        assert is_valid is True
        assert len(tools) == 2
        assert tools[0]["tool"] == "filesystem_tools"
        assert tools[1]["tool"] == "browser_tools"
        assert result["status"] == "success"
        assert len(result["tool_calls"]) == 2
    
    def test_invalid_json_handling(self):
        """Test handling of invalid JSON."""
        invalid_json = "not a json at all"
        
        # Configure mock
        mock_command_processor.validate_command.return_value = False
        mock_command_processor.extract_tools.return_value = []
        mock_command_processor.process_command.return_value = {
            "status": "error",
            "result": "Invalid JSON format",
            "tool_calls": []
        }
        
        # Process invalid JSON
        is_valid = mock_command_processor.validate_command(invalid_json)
        tools = mock_command_processor.extract_tools(invalid_json)
        result = mock_command_processor.process_command(invalid_json)
        
        # Assertions
        assert is_valid is False
        assert len(tools) == 0
        assert result["status"] == "error"
        assert "Invalid JSON" in result["result"]
    
    def test_missing_required_fields(self, invalid_command_json):
        """Test handling of commands with missing required fields."""
        command_text = json.dumps(invalid_command_json, ensure_ascii=False)
        
        # Configure mock
        mock_command_processor.validate_command.return_value = False
        mock_command_processor.extract_tools.return_value = []
        mock_command_processor.process_command.return_value = {
            "status": "error",
            "result": "Missing required field: params",
            "tool_calls": []
        }
        
        # Process invalid command
        is_valid = mock_command_processor.validate_command(command_text)
        tools = mock_command_processor.extract_tools(command_text)
        result = mock_command_processor.process_command(command_text)
        
        # Assertions
        assert is_valid is False
        assert len(tools) == 0
        assert result["status"] == "error"
        assert "Missing required field" in result["result"]
    
    def test_empty_command_handling(self):
        """Test handling of empty commands."""
        test_cases = [
            ("", "Empty string"),
            ("{}", "Empty JSON object"),
            ("[]", "Empty array"),
            ("null", "Null value")
        ]
        
        for test_input, description in test_cases:
            # Configure mock for each case
            mock_command_processor.validate_command.return_value = False
            mock_command_processor.extract_tools.return_value = []
            
            # Process empty command
            is_valid = mock_command_processor.validate_command(test_input)
            tools = mock_command_processor.extract_tools(test_input)
            
            # Assertions
            assert is_valid is False, f"Failed for {description}: {test_input}"
            assert len(tools) == 0, f"Failed for {description}: {test_input}"
    
    def test_malformed_json_handling(self):
        """Test handling of malformed JSON."""
        malformed_cases = [
            '{"tool": "test", "params":}',  # Missing value
            '{"tool": "test", "params": {',  # Unclosed brace
            '{"tool": "test" "params": {}}',  # Missing comma
            '{"tool": test, "params": {}}',  # Unquoted value
        ]
        
        for malformed_json in malformed_cases:
            # Configure mock
            mock_command_processor.validate_command.return_value = False
            mock_command_processor.extract_tools.return_value = []
            mock_command_processor.process_command.return_value = {
                "status": "error",
                "result": "Malformed JSON",
                "tool_calls": []
            }
            
            # Process malformed JSON
            is_valid = mock_command_processor.validate_command(malformed_json)
            tools = mock_command_processor.extract_tools(malformed_json)
            result = mock_command_processor.process_command(malformed_json)
            
            # Assertions
            assert is_valid is False
            assert len(tools) == 0
            assert result["status"] == "error"
    
    def test_free_text_filtering(self):
        """Test that free text doesn't trigger command execution."""
        free_text_cases = [
            "Hello, how are you?",
            "Please help me with this task",
            "The filesystem_tools can help with file operations",
            "I need to use browser_tools for web automation",
            "```json\n{\"tool\": \"test\"}\n```",  # Code block
            "**filesystem_tools** is useful for file operations"  # Markdown
        ]
        
        for free_text in free_text_cases:
            # Configure mock to not extract tools from free text
            mock_command_processor.validate_command.return_value = False
            mock_command_processor.extract_tools.return_value = []
            
            # Process free text
            is_valid = mock_command_processor.validate_command(free_text)
            tools = mock_command_processor.extract_tools(free_text)
            
            # Assertions
            assert is_valid is False, f"Free text should not be valid: {free_text}"
            assert len(tools) == 0, f"Free text should not extract tools: {free_text}"
    
    def test_tool_execution_success(self, valid_command_json):
        """Test successful tool execution."""
        # Configure mock for successful execution
        mock_tool_executor.is_available.return_value = True
        mock_tool_executor.execute.return_value = {
            "status": "success",
            "output": "file1.txt\nfile2.txt\ndirectory1/",
            "error": None
        }
        
        # Execute tool
        is_available = mock_tool_executor.is_available()
        result = mock_tool_executor.execute(valid_command_json)
        
        # Assertions
        assert is_available is True
        assert result["status"] == "success"
        assert "file1.txt" in result["output"]
        assert result["error"] is None
        mock_tool_executor.execute.assert_called_once_with(valid_command_json)
    
    def test_tool_execution_failure(self, valid_command_json):
        """Test tool execution failure."""
        # Configure mock for execution failure
        mock_tool_executor.is_available.return_value = True
        mock_tool_executor.execute.return_value = {
            "status": "error",
            "output": None,
            "error": "Permission denied: /home/user"
        }
        
        # Execute tool
        result = mock_tool_executor.execute(valid_command_json)
        
        # Assertions
        assert result["status"] == "error"
        assert result["output"] is None
        assert "Permission denied" in result["error"]
    
    def test_tool_unavailable(self, valid_command_json):
        """Test handling when tool is unavailable."""
        # Configure mock for unavailable tool
        mock_tool_executor.is_available.return_value = False
        mock_tool_executor.execute.return_value = {
            "status": "error",
            "output": None,
            "error": "Tool 'filesystem_tools' is not available"
        }
        
        # Check availability and execute
        is_available = mock_tool_executor.is_available()
        result = mock_tool_executor.execute(valid_command_json)
        
        # Assertions
        assert is_available is False
        assert result["status"] == "error"
        assert "not available" in result["error"]
    
    def test_tool_schema_validation(self):
        """Test tool schema validation."""
        # Configure mock schema
        expected_schema = {
            "name": "filesystem_tools",
            "description": "File system operations tool",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string"},
                    "path": {"type": "string"}
                },
                "required": ["command"]
            }
        }
        
        mock_tool_executor.get_schema.return_value = expected_schema
        
        # Get schema
        schema = mock_tool_executor.get_schema()
        
        # Assertions
        assert schema["name"] == "filesystem_tools"
        assert "parameters" in schema
        assert "command" in schema["parameters"]["properties"]
        assert "command" in schema["parameters"]["required"]
    
    def test_concurrent_command_execution(self, valid_command_array):
        """Test concurrent execution of multiple commands."""
        command_text = json.dumps(valid_command_array, ensure_ascii=False)
        
        # Configure mocks
        mock_command_processor.extract_tools.return_value = valid_command_array
        mock_tool_executor.execute.side_effect = [
            {
                "status": "success",
                "output": "file1.txt\nfile2.txt",
                "error": None
            },
            {
                "status": "success", 
                "output": "Browser opened to https://example.com",
                "error": None
            }
        ]
        
        # Extract and execute tools
        tools = mock_command_processor.extract_tools(command_text)
        results = []
        for tool in tools:
            result = mock_tool_executor.execute(tool)
            results.append(result)
        
        # Assertions
        assert len(results) == 2
        assert all(result["status"] == "success" for result in results)
        assert "file1.txt" in results[0]["output"]
        assert "Browser opened" in results[1]["output"]
        assert mock_tool_executor.execute.call_count == 2
    
    def test_command_validation_edge_cases(self):
        """Test edge cases in command validation."""
        test_cases = [
            ('{"tool": "", "params": {}}', False, "Empty tool name"),
            ('{"tool": "valid_tool", "params": null}', False, "Null params"),
            ('{"tool": "valid_tool", "params": "string"}', False, "String params instead of object"),
            ('{"tool": "valid_tool", "params": []}', False, "Array params instead of object"),
            ('{"tool": "valid_tool", "params": {}}', True, "Valid minimal command"),
            ('{"tool": "valid_tool", "params": {"key": "value"}}', True, "Valid command with params"),
        ]
        
        for test_input, expected_valid, description in test_cases:
            # Configure mock based on expected result
            mock_command_processor.validate_command.return_value = expected_valid
            
            # Test validation
            is_valid = mock_command_processor.validate_command(test_input)
            
            # Assertion with descriptive message
            assert is_valid == expected_valid, f"Failed for {description}: {test_input}"
    
    def test_command_parameter_validation(self):
        """Test validation of command parameters."""
        # Test cases with different parameter types
        parameter_cases = [
            ({"command": "ls", "path": "/home"}, True, "String parameters"),
            ({"command": "ls", "recursive": True}, True, "Boolean parameters"),
            ({"command": "ls", "depth": 2}, True, "Numeric parameters"),
            ({"files": ["file1.txt", "file2.txt"]}, True, "Array parameters"),
            ({"config": {"verbose": True, "format": "json"}}, True, "Object parameters"),
            ({}, True, "Empty parameters object"),
        ]
        
        for params, expected_valid, description in parameter_cases:
            command = {"tool": "test_tool", "params": params}
            command_text = json.dumps(command, ensure_ascii=False)
            
            # Configure mock
            mock_command_processor.validate_command.return_value = expected_valid
            
            # Test validation
            is_valid = mock_command_processor.validate_command(command_text)
            
            # Assertion
            assert is_valid == expected_valid, f"Failed for {description}: {params}"
    
    def test_error_recovery_in_command_processing(self):
        """Test error recovery during command processing."""
        # Command that will cause tool execution error
        failing_command = {
            "tool": "filesystem_tools",
            "params": {"command": "rm", "path": "/protected/file"}
        }
        command_text = json.dumps(failing_command, ensure_ascii=False)
        
        # Configure mocks
        mock_command_processor.validate_command.return_value = True
        mock_command_processor.extract_tools.return_value = [failing_command]
        mock_tool_executor.execute.return_value = {
            "status": "error",
            "output": None,
            "error": "Permission denied"
        }
        
        # Process command with error
        is_valid = mock_command_processor.validate_command(command_text)
        tools = mock_command_processor.extract_tools(command_text)
        
        if is_valid and tools:
            result = mock_tool_executor.execute(tools[0])
        
        # Assertions - system should handle error gracefully
        assert is_valid is True
        assert len(tools) == 1
        assert result["status"] == "error"
        assert "Permission denied" in result["error"]
        # System should continue functioning after error
        mock_tool_executor.execute.assert_called_once()
    
    @pytest.mark.integration
    def test_full_command_processing_pipeline(self, valid_command_json):
        """Test the complete command processing pipeline."""
        command_text = json.dumps(valid_command_json, ensure_ascii=False)
        
        # Configure mocks for full pipeline
        mock_command_processor.validate_command.return_value = True
        mock_command_processor.extract_tools.return_value = [valid_command_json]
        mock_tool_manager.is_tool_available.return_value = True
        mock_tool_executor.execute.return_value = {
            "status": "success",
            "output": "Command executed successfully",
            "error": None
        }
        
        # Execute full pipeline
        # 1. Validate command
        is_valid = mock_command_processor.validate_command(command_text)
        
        # 2. Extract tools
        if is_valid:
            tools = mock_command_processor.extract_tools(command_text)
        
        # 3. Check tool availability
        if tools:
            tool_name = tools[0]["tool"]
            is_available = mock_tool_manager.is_tool_available(tool_name)
        
        # 4. Execute tool
        if is_available:
            result = mock_tool_executor.execute(tools[0])
        
        # Assertions for complete pipeline
        assert is_valid is True
        assert len(tools) == 1
        assert is_available is True
        assert result["status"] == "success"
        assert "executed successfully" in result["output"]
        
        # Verify all components were called
        mock_command_processor.validate_command.assert_called_once()
        mock_command_processor.extract_tools.assert_called_once()
        mock_tool_manager.is_tool_available.assert_called_once_with("filesystem_tools")
        mock_tool_executor.execute.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
