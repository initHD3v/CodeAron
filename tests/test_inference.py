import unittest
import os
from src.llm.inference import InferenceEngine
from src.core.config import settings

class TestInferenceEngine(unittest.TestCase):
    def setUp(self):
        self.engine = InferenceEngine()

    def test_engine_initialization(self):
        """Memastikan engine terinisialisasi dengan path model yang benar."""
        self.assertIsNotNone(self.engine.model_path)
        # Pastikan path default mengarah ke model yang ada atau default settings
        self.assertTrue(len(self.engine.model_path) > 0)

    def test_singleton_config(self):
        """Memastikan settings terbaca dengan benar."""
        self.assertEqual(settings.APP_NAME, "CodeAron")

if __name__ == '__main__':
    unittest.main()
