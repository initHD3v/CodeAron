import os
import logging
from typing import List, Dict, Any
from fastembed import TextEmbedding
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchText
from src.core.config import settings

logger = logging.getLogger("VectorStore")

class VectorStore:
    def __init__(self):
        self.db_path = str(settings.DB_DIR)
        self.cache_dir = str(settings.MODEL_DIR / ".embeddings")
        os.makedirs(self.cache_dir, exist_ok=True)
        
        self.client = QdrantClient(path=self.db_path)
        self.collection_name = "code_symbols"
        self.model = None
        
        self._load_model()
        self._init_collection()

    def close(self):
        try:
            if hasattr(self, 'client'): self.client.close()
        except Exception as e:
            logger.error(f"Error closing Qdrant: {e}")

    def _load_model(self):
        try:
            self.model = TextEmbedding(
                model_name="BAAI/bge-small-en-v1.5",
                cache_dir=self.cache_dir
            )
        except Exception as e:
            logger.error(f"Embedding model error: {e}")
            raise RuntimeError("Semantic memory failed to load. Check internet/cache.")

    def _init_collection(self):
        try:
            collections = self.client.get_collections().collections
            if not any(c.name == self.collection_name for c in collections):
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
                )
        except Exception as e:
            logger.error(f"Collection init error: {e}")

    def add_symbols(self, symbols: List[Dict[str, Any]]):
        if not symbols or not self.model: return

        try:
            texts = [f"{s['name']} in {s['file_path']}: {s['content']}" for s in symbols]
            embeddings = list(self.model.embed(texts))
            
            points = []
            for i, (symbol, embedding) in enumerate(zip(symbols, embeddings)):
                points.append(PointStruct(
                    id=hash(f"{symbol['file_path']}_{symbol['name']}_{i}") & 0xFFFFFFFFFFFFFFFF,
                    vector=embedding.tolist(),
                    payload=symbol
                ))
            
            self.client.upsert(collection_name=self.collection_name, points=points)
        except Exception as e:
            logger.error(f"Upsert error: {e}")

    def clear_all(self):
        try:
            self.client.delete_collection(collection_name=self.collection_name)
            self._init_collection()
        except Exception as e:
            logger.error(f"Clear DB error: {e}")

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        try:
            if not self.model: return []
            query_embedding = list(self.model.embed([query]))[0]
            
            # Simple path filtering using native Qdrant filter
            must_not = [
                FieldCondition(key="file_path", match=MatchText(text=p)) 
                for p in settings.IGNORED_DIRS if len(p) > 2
            ]

            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding.tolist(),
                query_filter=Filter(must_not=must_not),
                limit=limit
            )
            return [res.payload for res in results if res.payload]
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
