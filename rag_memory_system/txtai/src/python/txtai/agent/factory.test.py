import unittest
from unittest.mock import MagicMock, patch

from smolagents import ToolCallingAgent

from agent_factory import ProcessFactory


class TestProcessFactory(unittest.TestCase):
    @patch("agent_factory.ProcessFactory.ToolFactory.create")
    @patch("agent_factory.ProcessFactory.PipelineModel")
    def test_create_default(self, mock_pipeline_model, mock_tool_factory):
        config = {"tool1": "tool1_config"}
        mock_tool_factory.create.return_value = ["tool1"]
        ProcessFactory.create(config)
        mock_pipeline_model.assert_called_once()

    @patch("agent_factory.ProcessFactory.ToolFactory.create")
    @patch("agent_factory.ProcessFactory.PipelineModel")
    def test_create_code_agent(self, mock_pipeline_model, mock_tool_factory):
        config = {"method": "code", "tool1": "tool1_config"}
        mock_tool_factory.create.return_value = ["tool1"]
        ProcessFactory.create(config)
        mock_pipeline_model.assert_called_once()

    @patch("agent_factory.ProcessFactory.ToolFactory.create")
    @patch("agent_factory.ProcessFactory.PipelineModel")
    def test_create_with_llm(self, mock_pipeline_model, mock_tool_factory):
        config = {"llm": "test_llm", "tool1": "tool1_config"}
        mock_tool_factory.create.return_value = ["tool1"]
        ProcessFactory.create(config)
        mock_pipeline_model.assert_called_once()

    @patch("agent_factory.ProcessFactory.ToolFactory.create")
    @patch("agent_factory.ProcessFactory.PipelineModel")
    def test_create_with_model_dict(self, mock_pipeline_model, mock_tool_factory):
        config = {"model": {"name": "test_model"}, "tool1": "tool1_config"}
        mock_tool_factory.create.return_value = ["tool1"]
        ProcessFactory.create(config)
        mock_pipeline_model.assert_called_once()

    @patch("agent_factory.ProcessFactory.ToolFactory.create")
    @patch("agent_factory.ProcessFactory.PipelineModel")
    def test_create_returns_tool_calling_agent(self, mock_pipeline_model, mock_tool_factory):
        config = {"tool1": "tool1_config"}
        mock_tool_factory.create.return_value = ["tool1"]
        mock_pipeline_model.return_value = MagicMock()
        agent = ProcessFactory.create(config)
        self.assertIsInstance(agent, ToolCallingAgent)