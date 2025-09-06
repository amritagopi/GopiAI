import unittest
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from .. import application
from ..api.tabular import router


class TestTabularAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(router)
        self.mock_app = MagicMock()
        self.mock_pipeline = MagicMock()
        self.mock_app.pipeline.return_value = self.mock_pipeline
        application.get = MagicMock(return_value=self.mock_app)

    def test_tabular_endpoint(self):
        self.mock_pipeline.return_value = [{"id": 1, "text": "test", "tag": "tag"}]
        response = self.client.get("/tabular?file=test_file")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [{"id": 1, "text": "test", "tag": "tag"}])
        self.mock_app.pipeline.assert_called_with("tabular", ("test_file",))

    def test_batchtabular_endpoint(self):
        self.mock_pipeline.return_value = [
            [{"id": 1, "text": "test1", "tag": "tag1"}],
            [{"id": 2, "text": "test2", "tag": "tag2"}],
        ]
        response = self.client.post("/batchtabular", json=["file1", "file2"])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            [
                [{"id": 1, "text": "test1", "tag": "tag1"}],
                [{"id": 2, "text": "test2", "tag": "tag2"}],
            ],
        )
        self.mock_app.pipeline.assert_called_with("tabular", (["file1", "file2"],))

    def test_batchtabular_empty_list(self):
        self.mock_pipeline.return_value = []
        response = self.client.post("/batchtabular", json=[])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])
        self.mock_app.pipeline.assert_called_with("tabular", ([],))

    def test_tabular_endpoint_no_file(self):
        with self.assertRaises(TypeError):
            self.client.get("/tabular")

    def test_batchtabular_no_body(self):
        response = self.client.post("/batchtabular")
        self.assertEqual(response.status_code, 422)