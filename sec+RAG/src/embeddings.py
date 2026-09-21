import time
from typing import List, Union
import numpy as np
from sentence_transformers import SentenceTransformer
from src.config import EMBEDDING_MODEL_NAME

_MODEL_INSTANCE = None

def get_embedding_model() -> SentenceTransformer:
    """Singleton getter for cached embedding model."""
    global _MODEL_INSTANCE
    if _MODEL_INSTANCE is None:
        start = time.perf_counter()
        _MODEL_INSTANCE = SentenceTransformer(EMBEDDING_MODEL_NAME)
        elapsed = (time.perf_counter() - start) * 1000
        print(f"[EMBEDDINGS] Loaded model {EMBEDDING_MODEL_NAME} in {elapsed:.2f} ms")
    return _MODEL_INSTANCE

def embed_query(query: str) -> np.ndarray:
    """Embed a single query string."""
    model = get_embedding_model()
    return model.encode(query, convert_to_numpy=True, normalize_embeddings=True)

def embed_documents(texts: List[str], batch_size: int = 64) -> np.ndarray:
    """Embed a list of document strings in batches."""
    model = get_embedding_model()
    return model.encode(
        texts, 
        batch_size=batch_size, 
        show_progress_bar=True, 
        convert_to_numpy=True, 
        normalize_embeddings=True
    )
