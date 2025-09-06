import unittest

from txtai.ann import ANN


class TestANN(unittest.TestCase):
    def test_init(self):
        config = {"backend": "test"}
        ann = ANN(config)
        self.assertEqual(ann.config, config)
        self.assertIsNone(ann.backend)

    def test_setting(self):
        config = {"backend": "test", "test": {"setting1": "value1"}}
        ann = ANN(config)
        self.assertEqual(ann.setting("setting1"), "value1")
        self.assertEqual(ann.setting("setting2", "default"), "default")

    def test_metadata(self):
        config = {"backend": "test"}
        ann = ANN(config)
        ann.metadata({"setting1": "value1"})
        self.assertIn("build", ann.config)
        self.assertIn("update", ann.config)

    def test_abstract_methods(self):
        config = {"backend": "test"}
        ann = ANN(config)
        with self.assertRaises(NotImplementedError):
            ann.load("path")
        with self.assertRaises(NotImplementedError):
            ann.index("embeddings")
        with self.assertRaises(NotImplementedError):
            ann.append("embeddings")
        with self.assertRaises(NotImplementedError):
            ann.delete("ids")
        with self.assertRaises(NotImplementedError):
            ann.search("queries", 10)
        with self.assertRaises(NotImplementedError):
            ann.count()
        with self.assertRaises(NotImplementedError):
            ann.save("path")

    def test_close(self):
        config = {"backend": "test"}
        ann = ANN(config)
        ann.backend = "some_backend"
        ann.close()
        self.assertIsNone(ann.backend)