import time
import os
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from src.config import VECTORSTORE_DIR, CHROMA_COLLECTION_NAME, DEFAULT_TOP_K, RELEVANCE_THRESHOLD
from src.embeddings import embed_query, embed_documents

class GRCRetriever:
    """Persistent local vector retriever backed by ChromaDB."""

    def __init__(self, vectorstore_dir: str = str(VECTORSTORE_DIR)):
        self.vectorstore_dir = str(vectorstore_dir)
        self.client = chromadb.PersistentClient(path=self.vectorstore_dir)
        self.collection = None
        self._get_or_create_collection()

    def _get_or_create_collection(self):
        """Get or initialize the Chroma collection with cosine distance metric."""
        try:
            self.collection = self.client.get_collection(
                name=CHROMA_COLLECTION_NAME
            )
        except Exception:
            self.collection = self.client.create_collection(
                name=CHROMA_COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"}
            )

    def is_indexed(self) -> bool:
        """Check if vectorstore exists and contains documents."""
        try:
            return self.collection is not None and self.collection.count() > 0
        except Exception:
            return False

    def document_count(self) -> int:
        """Return count of indexed documents."""
        if self.collection:
            return self.collection.count()
        return 0

    def build_index(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Embeds documents ONCE and persists them into ChromaDB vectorstore.
        """
        start_time = time.perf_counter()
        
        # Reset collection if re-building
        try:
            self.client.delete_collection(name=CHROMA_COLLECTION_NAME)
        except Exception:
            pass
            
        self.collection = self.client.create_collection(
            name=CHROMA_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )

        search_texts = [doc["search_text"] for doc in documents]
        ids = [doc["doc_id"] for doc in documents]
        metadatas = [
            {
                "framework": doc["framework"],
                "control_id": doc["control_id"],
                "title": doc["title"],
                "source": doc["source"],
                "document_type": doc["document_type"]
            }
            for doc in documents
        ]
        contents = [doc["content"] for doc in documents]

        print(f"[RETRIEVER] Generating embeddings for {len(documents)} documents...")
        embeddings = embed_documents(search_texts)
        embeddings_list = embeddings.tolist()

        print(f"[RETRIEVER] Storing in ChromaDB at {self.vectorstore_dir}...")
        
        # Add in batches to avoid memory overhead
        batch_size = 500
        for i in range(0, len(documents), batch_size):
            self.collection.add(
                ids=ids[i:i+batch_size],
                embeddings=embeddings_list[i:i+batch_size],
                metadatas=metadatas[i:i+batch_size],
                documents=contents[i:i+batch_size]
            )

        elapsed = time.perf_counter() - start_time
        return {
            "documents_indexed": len(documents),
            "build_time_seconds": round(elapsed, 2),
            "index_path": self.vectorstore_dir
        }

    def retrieve(
        self, 
        query: str, 
        top_k: int = DEFAULT_TOP_K, 
        threshold: float = RELEVANCE_THRESHOLD
    ) -> Dict[str, Any]:
        """
        Retrieves top_k relevant controls for a given user query.
        Returns exact latency, similarity scores, and evidence status.
        """
        start_time = time.perf_counter()
        
        if not self.is_indexed():
            raise RuntimeError("Knowledge base not initialized. Run: python scripts/build_index.py")

        # 1. Embed query
        query_vector = embed_query(query).tolist()
        
        # 2. Vector search in ChromaDB
        results = self.collection.query(
            query_embeddings=[query_vector],
            n_results=min(top_k, self.document_count())
        )
        
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        retrieved_docs = []
        has_evidence = False

        if results and results.get("ids") and len(results["ids"][0]) > 0:
            distances = results["distances"][0]
            metadatas = results["metadatas"][0]
            contents = results["documents"][0]
            ids = results["ids"][0]

            for i in range(len(ids)):
                distance = distances[i]
                # Cosine similarity conversion (1 - distance for cosine space in Chroma)
                similarity = max(0.0, min(1.0, 1.0 - distance))
                meta = metadatas[i]
                
                doc_item = {
                    "doc_id": ids[i],
                    "framework": meta.get("framework", "N/A"),
                    "control_id": meta.get("control_id", "N/A"),
                    "title": meta.get("title", "N/A"),
                    "content": contents[i],
                    "source": meta.get("source", "N/A"),
                    "similarity_score": round(similarity, 4),
                    "distance": round(distance, 4),
                    "passes_threshold": similarity >= threshold
                }
                retrieved_docs.append(doc_item)

        # Check if any document passes the relevance threshold
        passed_docs = [d for d in retrieved_docs if d["passes_threshold"]]
        has_evidence = len(passed_docs) > 0

        return {
            "query": query,
            "retrieved_docs": retrieved_docs,
            "passed_docs": passed_docs,
            "has_evidence": has_evidence,
            "retrieval_time_ms": round(elapsed_ms, 2),
            "total_searched": self.document_count(),
            "threshold_used": threshold
        }
