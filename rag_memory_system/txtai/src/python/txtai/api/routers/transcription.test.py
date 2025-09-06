import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI

from typing import List


class MockApplication:
    def __init__(self):
        self.pipeline_mock = MagicMock()

    def pipeline(self, task_name, data):
        return self.pipeline_mock(task_name, data)

class TestTranscriptionEndpoints(unittest.TestCase):

    def setUp(self):
        from .. import api
        self.app = FastAPI()
        self.app.include_router(api.router)
        self.client = TestClient(self.app)
        self.mock_app = MockApplication()

    @patch("src.api.application.get")
    def test_transcribe_endpoint(self, mock_get_app):
        mock_get_app.return_value = self.mock_app
        self.mock_app.pipeline_mock.return_value = "transcribed text"
        response = self.client.get("/transcribe?file=test.wav")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), "transcribed text")
        self.mock_app.pipeline_mock.assert_called_once_with("transcription", ("test.wav",))

    @patch("src.api.application.get")
    def test_batchtranscribe_endpoint(self, mock_get_app):
        mock_get_app.return_value = self.mock_app
        self.mock_app.pipeline_mock.return_value = ["transcribed text 1", "transcribed text 2"]
        files = ["test1.wav", "test2.wav"]
        response = self.client.post("/batchtranscribe", json=files)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), ["transcribed text 1", "transcribed text 2"])
        self.mock_app.pipeline_mock.assert_called_once_with("transcription", (files,))

    @patch("src.api.application.get")
    def test_transcribe_endpoint_empty_file(self, mock_get_app):
        mock_get_app.return_value = self.mock_app
        self.mock_app.pipeline_mock.return_value = ""
        response = self.client.get("/transcribe?file=")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), "")
        self.mock_app.pipeline_mock.assert_called_once_with("transcription", ("",))

    @patch("src.api.application.get")
    def test_batchtranscribe_endpoint_empty_list(self, mock_get_app):
        mock_get_app.return_value = self.mock_app
        self.mock_app.pipeline_mock.return_value = []
        files: List[str] = []
        response = self.client.post("/batchtranscribe", json=files)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])
        self.mock_app.pipeline_mock.assert_called_once_with("transcription", (files,))

    @patch("src.api.application.get")
    def test_batchtranscribe_endpoint_missing_body(self, mock_get_app):
        mock_get_app.return_value = self.mock_app
        response = self.client.post("/batchtranscribe")
        self.assertEqual(response.status_code, 422)