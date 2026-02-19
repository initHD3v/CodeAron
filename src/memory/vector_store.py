import os
import logging
import hashlib
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
        
        # Buat nama koleksi unik per proyek menggunakan hash path
        project_hash = hashlib.md5(str(settings.CURRENT_PROJECT_DIR).encode()).hexdigest()[:12]
        self.collection_name = f"code_symbols_{project_hash}"
        
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
            qv = query_embedding.tolist()
            
            # Refined filtering: only exclude if a path segment exactly matches an ignored dir
            must_not = []
            for p in settings.IGNORED_DIRS:
                if len(p) > 1:
                    must_not.append(FieldCondition(key="file_path", match=MatchText(text=p)))

            # Gunakan query_points jika tersedia (qdrant-client >= 1.7.0)
            # Fallback ke search jika gagal
            try:
                results = self.client.query_points(
                    collection_name=self.collection_name,
                    query=qv,
                    query_filter=Filter(must_not=must_not) if must_not else None,
                    limit=limit,
                    with_payload=True
                ).points
            except AttributeError:
                results = self.client.search(
                    collection_name=self.collection_name,
                    query_vector=qv,
                    query_filter=Filter(must_not=must_not) if must_not else None,
                    limit=limit,
                    with_payload=True
                )
            
            return [res.payload for res in results if res.payload]
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []

    def count_points(self) -> int:
        try:
            return self.client.get_collection(self.collection_name).points_count
        except:
            return 0
