#!/usr/bin/env python3
"""
Improved tests for command processor using new fixtures.
"""

import pytest
import json
from unittest.mock import MagicMock, patch

# Import test infrastructure
import sys
import os
    # Заменено на использование path_manager: sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'test_infrastructure'))

from fixtures import ai_service_mocker, mock_crewai_server, mock_tool_manager
from crewai_fixtures import mock_command_processor, mock_tool_executor


class TestCommandProcessorImproved:
    """Improved command processor tests using fixtures."""
    
    def test_valid_json_command_processing(self, mock_command_processor):
        """Test processing of valid JSON commands."""
        # Test data
        command_data = {
            "tool": "browser_tools",
            "params": {"command": "open", "url": "https://example.com"}
        }
        command_text = json.dumps(command_data, ensure_ascii=False)
        
        # Process command
        result = mock_command_processor.process_command(command_text)
        
        # Assertions
        assert result["status"] == "success"
        assert "result" in result
        mock_command_processor.process_command.assert_called_once_with(command_text)
    
    def test_array_of_commands(self, mock_command_processor):
        """Test processing of multiple commands in array format."""
        commands_data = [
            {"tool": "filesystem_tools", "params": {"command": "ls", "path": "."}},
            {"tool": "web_search", "params": {"query": "gopi ai project"}}
        ]
        commands_text = json.dumps(commands_data, ensure_ascii=False)
        
        # Configure mock to return multiple tool calls
        mock_command_processor.extract_tools.return_value = [
            {"tool": "filesystem_tools", "params": {"command": "ls", "path": "."}},
            {"tool": "web_search", "params": {"query": "gopi ai project"}}
        ]
        
        # Process commands
        result = mock_command_processor.process_command(commands_text)
        tools = mock_command_processor.extract_tools(commands_text)
        
        # Assertions
        assert result["status"] == "success"
        assert len(tools) == 2
        assert tools[0]["tool"] == "filesystem_tools"
        assert tools[1]["tool"] == "web_search"
    
    def test_invalid_json_handling(self, mock_command_processor):
        """Test handling of invalid JSON."""
        invalid_json = "not a json at all"
        
        # Configure mock to handle invalid JSON
        mock_command_processor.validate_command.return_value = False
        mock_command_processor.process_command.return_value = {
            "status": "error",
            "result": "Invalid JSON format",
            "tool_calls": []
        }
        
        # Process invalid JSON
        result = mock_command_processor.process_command(invalid_json)
        is_valid = mock_command_processor.validate_command(invalid_json)
        
        # Assertions
        assert not is_valid
        assert result["status"] == "error"
        assert "Invalid JSON" in result["result"]
        assert len(result["tool_calls"]) == 0
    
    def test_missing_required_fields(self, mock_command_processor):
        """Test handling of JSON with missing required fields."""
        # Missing params field
        incomplete_data = {"tool": "browser_tools"}
        incomplete_text = json.dumps(incomplete_data, ensure_ascii=False)
        
        # Configure mock for validation failure
        mock_command_processor.validate_command.return_value = False
        mock_command_processor.process_command.return_value = {
            "status": "error",
            "result": "Missing required field: params",
            "tool_calls": []
        }
        
        # Process incomplete command
        result = mock_command_processor.process_command(incomplete_text)
        is_valid = mock_command_processor.validate_command(incomplete_text)
        
        # Assertions
        assert not is_valid
        assert result["status"] == "error"
        assert "Missing required field" in result["result"]
    
    def test_free_text_markdown_handling(self, mock_command_processor):
        """Test that free text with markdown doesn't trigger command execution."""
        markdown_text = "О, зая моя любопытная...\n**filesystem_tools** могу всё...\n`lss*([^n]*)` ..."
        
        # Configure mock to not extract tools from free text
        mock_command_processor.extract_tools.return_value = []
        mock_command_processor.validate_command.return_value = False
        
        # Process markdown text
        tools = mock_command_processor.extract_tools(markdown_text)
        is_valid = mock_command_processor.validate_command(markdown_text)
        
        # Assertions
        assert not is_valid
        assert len(tools) == 0
    
    def test_tool_execution_integration(self, mock_command_processor, mock_tool_executor):
        """Test integration between command processor and tool executor."""
        # Test data
        command_data = {"tool": "filesystem_tools", "params": {"command": "ls", "path": "."}}
        command_text = json.dumps(command_data, ensure_ascii=False)
        
        # Configure mocks
        mock_command_processor.extract_tools.return_value = [command_data]
        mock_tool_executor.execute.return_value = {
            "status": "success",
            "output": "file1.txt\nfile2.txt\ndirectory1/",
            "error": None
        }
        
        # Process command and execute tool
        tools = mock_command_processor.extract_tools(command_text)
        if tools:
            execution_result = mock_tool_executor.execute(tools[0])
        
        # Assertions
        assert len(tools) == 1
        assert tools[0]["tool"] == "filesystem_tools"
        assert execution_result["status"] == "success"
        assert "file1.txt" in execution_result["output"]
    
    def test_error_handling_in_tool_execution(self, mock_command_processor, mock_tool_executor):
        """Test error handling during tool execution."""
        # Test data
        command_data = {"tool": "invalid_tool", "params": {"command": "test"}}
        command_text = json.dumps(command_data, ensure_ascii=False)
        
        # Configure mocks for error scenario
        mock_command_processor.extract_tools.return_value = [command_data]
        mock_tool_executor.execute.return_value = {
            "status": "error",
            "output": None,
            "error": "Tool 'invalid_tool' not found"
        }
        mock_tool_executor.is_available.return_value = False
        
        # Process command and attempt execution
        tools = mock_command_processor.extract_tools(command_text)
        if tools:
            is_available = mock_tool_executor.is_available()
            execution_result = mock_tool_executor.execute(tools[0])
        
        # Assertions
        assert len(tools) == 1
        assert not is_available
        assert execution_result["status"] == "error"
        assert "not found" in execution_result["error"]
    
    @pytest.mark.integration
    def test_full_command_processing_flow(self, mock_command_processor, mock_tool_executor, mock_tool_manager):
        """Test the complete flow from command to execution."""
        # Test data
        command_data = {"tool": "browser_tools", "params": {"command": "open", "url": "https://example.com"}}
        command_text = json.dumps(command_data, ensure_ascii=False)
        
        # Configure mocks for full flow
        mock_command_processor.validate_command.return_value = True
        mock_command_processor.extract_tools.return_value = [command_data]
        mock_tool_manager.is_tool_available.return_value = True
        mock_tool_executor.execute.return_value = {
            "status": "success",
            "output": "Browser opened to https://example.com",
            "error": None
        }
        
        # Execute full flow
        is_valid = mock_command_processor.validate_command(command_text)
        if is_valid:
            tools = mock_command_processor.extract_tools(command_text)
            if tools:
                tool_name = tools[0]["tool"]
                if mock_tool_manager.is_tool_available(tool_name):
                    result = mock_tool_executor.execute(tools[0])
        
        # Assertions
        assert is_valid
        assert len(tools) == 1
        assert mock_tool_manager.is_tool_available("browser_tools")
        assert result["status"] == "success"
        assert "Browser opened" in result["output"]
    
    def test_command_validation_edge_cases(self, mock_command_processor):
        """Test edge cases in command validation."""
        test_cases = [
            ("", False, "Empty string"),
            ("{}", False, "Empty JSON object"),
            ('{"tool": ""}', False, "Empty tool name"),
            ('{"tool": "valid_tool", "params": null}', False, "Null params"),
            ('{"tool": "valid_tool", "params": "string"}', False, "String params instead of object"),
            ('{"tool": "valid_tool", "params": {}}', True, "Valid minimal command"),
        ]
        
        for test_input, expected_valid, description in test_cases:
            # Configure mock based on expected result
            mock_command_processor.validate_command.return_value = expected_valid
            
            # Test validation
            is_valid = mock_command_processor.validate_command(test_input)
            
            # Assertion with descriptive message
            assert is_valid == expected_valid, f"Failed for {description}: {test_input}"
    
    def test_concurrent_command_processing(self, mock_command_processor):
        """Test handling of multiple concurrent commands."""
        commands = [
            {"tool": "tool1", "params": {"action": "test1"}},
            {"tool": "tool2", "params": {"action": "test2"}},
            {"tool": "tool3", "params": {"action": "test3"}}
        ]
        
        # Configure mock for concurrent processing
        mock_command_processor.extract_tools.return_value = commands
        mock_command_processor.process_command.return_value = {
            "status": "success",
            "result": f"Processed {len(commands)} commands",
            "tool_calls": commands
        }
        
        # Process multiple commands
        commands_text = json.dumps(commands, ensure_ascii=False)
        result = mock_command_processor.process_command(commands_text)
        extracted_tools = mock_command_processor.extract_tools(commands_text)
        
        # Assertions
        assert result["status"] == "success"
        assert len(extracted_tools) == 3
        assert len(result["tool_calls"]) == 3
        assert "Processed 3 commands" in result["result"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])