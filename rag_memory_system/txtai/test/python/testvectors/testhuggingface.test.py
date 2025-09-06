import unittest

import numpy as np

from txtai.vectors import VectorsFactory


class TestHFVectors(unittest.TestCase):
    """
    HFVectors tests
    """

    @classmethod
    def setUpClass(cls):
        """
        Create HFVectors instance.
        """

        cls.model = VectorsFactory.create({"path": "sentence-transformers/nli-mpnet-base-v2"}, None)

    def testIndex(self):
        documents = [(x, "This is a test", None) for x in range(100)]
        ids, dimension, batches, stream = self.model.index(documents)
        self.assertEqual(len(ids), 100)
        self.assertEqual(dimension, 768)

    def testText(self):
        self.model.tokenize = True
        self.assertEqual(self.model.prepare("Y 123 This is a test!"), "test")

    def testTransform(self):
        documents = [(0, "This is a test and has no tokenization", None), (1, "test tokenization", None)]
        self.model.tokenize = True
        embeddings1 = [self.model.transform(d) for d in documents]
        self.model.tokenize = False
        embeddings2 = [self.model.transform(d) for d in documents]
        self.assertFalse(np.array_equal(embeddings1[0], embeddings2[0]))

    def testTransformArray(self):
        data1 = np.random.rand(5, 5).astype(np.float32)
        data2 = self.model.transform((0, data1, None))
        self.assertTrue(np.array_equal(data1, data2))

    def testTransformLong(self):
        documents = [(0, "This is long text " * 512, None), (1, "This is short text", None)]
        embeddings = [self.model.transform(d) for d in documents]
        self.assertIsNotNone(embeddings)