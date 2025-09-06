import unittest
from unittest.mock import patch

from vectordb.index.ann import ANNFactory
from vectordb.index.ann.annoy import Annoy
from vectordb.index.ann.faiss import Faiss
from vectordb.index.ann.hnsw import HNSW


class TestANNFactory(unittest.TestCase):

    def test_create_default(self):
        config = {}
        ann = ANNFactory.create(config)
        self.assertIsInstance(ann, Faiss)
        self.assertEqual(config["backend"], "faiss")

    def test_create_annoy(self):
        config = {"backend": "annoy"}
        ann = ANNFactory.create(config)
        self.assertIsInstance(ann, Annoy)
        self.assertEqual(config["backend"], "annoy")

    def test_create_hnsw(self):
        config = {"backend": "hnsw"}
        ann = ANNFactory.create(config)
        self.assertIsInstance(ann, HNSW)
        self.assertEqual(config["backend"], "hnsw")

    def test_resolve_success(self):
        with patch("vectordb.index.ann.ANNFactory.resolve") as mock_resolve:
            config = {"backend": "custom"}
            mock_resolve.return_value = "resolved_ann"
            ann = ANNFactory.create(config)
            self.assertEqual(ann, "resolved_ann")
            self.assertEqual(config["backend"], "custom")

    def test_resolve_failure(self):
        with self.assertRaises(ImportError):
            ANNFactory.resolve("invalid_backend", {})