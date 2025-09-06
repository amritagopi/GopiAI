import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from ..api import summary


class TestSummaryAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(summary.router)

    @patch("app.application.get")
    def test_summary_endpoint(self, mock_get):
        mock_get.return_value.pipeline.return_value = "test summary"
        response = self.client.get("/summary?text=test")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), "test summary")

    @patch("app.application.get")
    def test_batchsummary_endpoint(self, mock_get):
        mock_get.return_value.pipeline.return_value = ["test summary 1", "test summary 2"]
        response = self.client.post("/batchsummary", json={"texts": ["test1", "test2"]})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), ["test summary 1", "test summary 2"])

    @patch("app.application.get")
    def test_summary_endpoint_with_lengths(self, mock_get):
        mock_get.return_value.pipeline.return_value = "test summary"
        response = self.client.get("/summary?text=test&minlength=10&maxlength=20")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), "test summary")

    @patch("app.application.get")
    def test_batchsummary_endpoint_with_lengths(self, mock_get):
        mock_get.return_value.pipeline.return_value = ["test summary 1", "test summary 2"]
        response = self.client.post("/batchsummary", json={"texts": ["test1", "test2"], "minlength": 10, "maxlength": 20})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), ["test summary 1", "test summary 2"])