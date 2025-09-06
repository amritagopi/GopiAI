import unittest
from unittest.mock import MagicMock

from smolagents import ChatMessage
from your_module import PipelineModel  # Replace your_module


class TestPipelineModel(unittest.TestCase):

    def test_init(self):
        llm_mock = MagicMock()
        model = PipelineModel(path=llm_mock)
        self.assertEqual(model.model_id, llm_mock.generator.path)

    def test_generate(self):
        llm_mock = MagicMock()
        llm_mock.return_value = "Test response"
        model = PipelineModel(path=llm_mock)
        message = model.generate([{"role": "user", "content": "Test"}])
        self.assertIsInstance(message, ChatMessage)
        self.assertEqual(message.content, "Test response")

    def test_generate_with_stop_sequences(self):
        llm_mock = MagicMock()
        llm_mock.return_value = "Test response stop"
        model = PipelineModel(path=llm_mock)
        message = model.generate([{"role": "user", "content": "Test"}], stop_sequences=["stop"])
        self.assertIsInstance(message, ChatMessage)
        self.assertEqual(message.content, "Test response ")

    def test_parameters(self):
        llm_mock = MagicMock()
        model = PipelineModel(path=llm_mock)
        model.parameters(1024)
        self.assertEqual(model.maxlength, 1024)

    def test_clean(self):
        llm_mock = MagicMock()
        model = PipelineModel(path=llm_mock)
        messages = [{"role": "user", "content": "Test"}]
        cleaned_messages = model.clean(messages)
        self.assertEqual(cleaned_messages, messages)


if __name__ == '__main__':
    unittest.main()