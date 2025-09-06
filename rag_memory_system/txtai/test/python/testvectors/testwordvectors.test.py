import unittest
from unittest.mock import patch
from txtai.vectors import VectorsFactory

class TestWordVectorsUnit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = "neuml/glove-6B-quantized"

    def test_lookup(self):
        model = VectorsFactory.create({"path": self.path}, None)
        self.assertEqual(model.lookup(["txtai", "embeddings"]).shape, (2, 300))

    @patch("os.cpu_count")
    def test_index_batch_size(self, cpucount):
        cpucount.return_value = 1
        documents = [(x, "test", None) for x in range(100)]
        model = VectorsFactory.create({"path": self.path, "parallel": True}, None)
        ids, dimension, batches, stream = model.index(documents, 20)
        self.assertEqual(batches, 5)

    def test_no_exist(self):
        with self.assertRaises(Exception):
            VectorsFactory.create({"method": "words", "path": "noexist"}, None)

    def test_transform_shape(self):
        model = VectorsFactory.create({"path": self.path}, None)
        vector = model.transform((None, ["txtai"], None))
        self.assertEqual(len(vector), 300)