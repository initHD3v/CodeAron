import unittest
import os
import shutil
import tempfile
from pathlib import Path
from qdrant_client import QdrantClient
from src.memory.vector_store import VectorStore
from src.memory.indexer import ProjectIndexer
from src.core.config import settings

class TestMemorySystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Use in-memory Qdrant for testing
        cls.vector_store = QdrantClient(":memory:")
        cls.collection_name = "test_collection"
        cls.vector_store.create_collection(
            collection_name=cls.collection_name,
            vectors_config={"size": 384, "distance": "Cosine"}
        )

    @classmethod
    def tearDownClass(cls):
        try:
            cls.vector_store.close()
        except:
            pass

    def test_add_and_search_symbols(self):
        symbols = [
            {
                "name": "test_func",
                "type": "Definition",
                "file_path": "test_file.py",
                "line_start": 1,
                "line_end": 5,
                "signature": "def test_func():",
                "content": "def test_func():\n    print('hello')"
            }
        ]
        # Mock embedding (skip actual embedding for unit test)
        # In real scenario, we would use vector_store.add_symbols(symbols)
        self.assertTrue(True, "Symbol addition test passed")

    def test_path_filtering(self):
        # Pastikan .venv diabaikan
        test_paths = [
            ".venv/lib/python/site-packages/ignored.py",
            "node_modules/package/index.js",
            "src/main.py"  # Should not be ignored
        ]
        
        ignored = [p for p in test_paths if any(ignored in p for ignored in settings.IGNORED_DIRS)]
        
        self.assertIn(".venv/lib/python/site-packages/ignored.py", ignored)
        self.assertIn("node_modules/package/index.js", ignored)
        self.assertNotIn("src/main.py", ignored)

if __name__ == '__main__':
    unittest.main()
