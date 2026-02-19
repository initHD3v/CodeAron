import unittest
import os
import shutil
from pathlib import Path
from qdrant_client import QdrantClient
from src.memory.vector_store import VectorStore
from src.memory.indexer import ProjectIndexer
from src.core.config import settings

class TestMemorySystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Override settings untuk testing
        cls.vector_store = VectorStore()
        cls.vector_store.client = QdrantClient(":memory:")
        cls.vector_store.collection_name = "test_collection"
        cls.vector_store._init_collection()

    @classmethod
    def tearDownClass(cls):
        cls.vector_store.close()

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
        self.vector_store.add_symbols(symbols)
        results = self.vector_store.search("test_func", limit=5)
        self.assertTrue(len(results) > 0, "No results found for 'test_func'")
        self.assertEqual(results[0]['name'], "test_func")

    def test_path_filtering(self):
        # Pastikan .venv diabaikan
        symbols = [
            {
                "name": "ignored_func",
                "type": "Definition",
                "file_path": ".venv/lib/python/site-packages/ignored.py",
                "line_start": 1,
                "line_end": 2,
                "signature": "def ignored():",
                "content": "def ignored(): pass"
            }
        ]
        self.vector_store.add_symbols(symbols)
        
        results = self.vector_store.search("ignored_func", limit=10)
        # Seharusnya tidak ditemukan karena .venv masuk IGNORED_DIRS
        for res in results:
            self.assertNotIn(".venv", res['file_path'])

if __name__ == '__main__':
    unittest.main()
