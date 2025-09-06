import unittest
from unittest.mock import MagicMock
from smolagents.tools.function_tool import FunctionTool


class TestFunctionTool(unittest.TestCase):
    def test_function_tool_initialization(self):
        mock_target = MagicMock()
        config = {
            "name": "test_tool",
            "description": "test_description",
            "inputs": ["input1", "input2"],
            "output": "test_output",
            "target": mock_target,
        }
        tool = FunctionTool(config)
        self.assertEqual(tool.name, "test_tool")
        self.assertEqual(tool.description, "test_description")
        self.assertEqual(tool.inputs, ["input1", "input2"])
        self.assertEqual(tool.output_type, "test_output")
        self.assertEqual(tool.target, mock_target)
        self.assertTrue(tool.skip_forward_signature_validation)

    def test_function_tool_forward_with_args_and_kwargs(self):
        mock_target = MagicMock(return_value="test_result")
        config = {
            "name": "test_tool",
            "description": "test_description",
            "inputs": ["input1", "input2"],
            "output": "test_output",
            "target": mock_target,
        }
        tool = FunctionTool(config)
        result = tool.forward("arg1", "arg2", kwarg1="kwarg1_value", kwarg2="kwarg2_value")
        self.assertEqual(result, "test_result")
        mock_target.assert_called_once_with("arg1", "arg2", kwarg1="kwarg1_value", kwarg2="kwarg2_value")

    def test_function_tool_forward_with_only_args(self):
        mock_target = MagicMock(return_value="test_result")
        config = {
            "name": "test_tool",
            "description": "test_description",
            "inputs": ["input1", "input2"],
            "output": "test_output",
            "target": mock_target,
        }
        tool = FunctionTool(config)
        result = tool.forward("arg1", "arg2")
        self.assertEqual(result, "test_result")
        mock_target.assert_called_once_with("arg1", "arg2")

    def test_function_tool_forward_with_only_kwargs(self):
        mock_target = MagicMock(return_value="test_result")
        config = {
            "name": "test_tool",
            "description": "test_description",
            "inputs": ["input1", "input2"],
            "output": "test_output",
            "target": mock_target,
        }
        tool = FunctionTool(config)
        result = tool.forward(kwarg1="kwarg1_value", kwarg2="kwarg2_value")
        self.assertEqual(result, "test_result")
        mock_target.assert_called_once_with(kwarg1="kwarg1_value", kwarg2="kwarg2_value")

    def test_function_tool_initialization_with_output_type(self):
        mock_target = MagicMock()
        config = {
            "name": "test_tool",
            "description": "test_description",
            "inputs": ["input1", "input2"],
            "output_type": "test_output_type",
            "target": mock_target,
        }
        tool = FunctionTool(config)
        self.assertEqual(tool.output_type, "test_output_type")
