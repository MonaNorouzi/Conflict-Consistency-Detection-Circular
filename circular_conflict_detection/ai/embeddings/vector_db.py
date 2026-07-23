import os
from typing import List, Dict, Any
try:
    import chromadb
except ImportError:
    raise ImportError("Please install chromadb (pip install chromadb)")


class CircularVectorDB:
    """
    Handles ChromaDB initialization, document upsertion, and semantic search.
    """
    def __init__(self, collection_name: str = "circular_clauses", persist_directory: str = "./chroma_data"):
        # Ensure the persistence directory exists
        os.makedirs(persist_directory, exist_ok=True)
        
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # We use cosine similarity (cosine) for semantic search
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def upsert_clauses(self, clauses: List[Dict[str, Any]], embeddings: List[List[float]]) -> None:
        """
        Stores parsed clauses and their embeddings in ChromaDB.
        
        Args:
            clauses (List[Dict]): The output directly from CircularParser.
            embeddings (List[List[float]]): The output directly from EmbeddingService.
        """
        if not clauses or not embeddings or len(clauses) != len(embeddings):
            raise ValueError("Clauses and embeddings lists must be non-empty and of the same length.")

        ids = []
        documents = []
        metadatas = []

        for clause in clauses:
            doc_id = clause.get("metadata", {}).get("doc_id", "unknown_doc")
            clause_id = clause.get("clause_id", "unknown_clause")
            
            # Create a unique ID for ChromaDB (e.g., "CIRC-1402-001_ماده ۱")
            ids.append(f"{doc_id}_{clause_id}")
            documents.append(clause["text"])
            metadatas.append(clause.get("metadata", {}))

        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )

    def search_similar_clauses(self, query_embedding: List[float], top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieves the most semantically similar clauses from the archive.
        
        Args:
            query_embedding (List[float]): A single vector representing the new clause.
            top_k (int): Number of closest matches to return.
            
        Returns:
            List[Dict]: Standardized list of retrieved clauses with similarity scores.
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        retrieved_clauses = []
        
        # ChromaDB returns nested lists. We extract the first index since we sent a single query.
        if results['ids'] and results['ids'][0]:
            for i in range(len(results['ids'][0])):
                retrieved_clauses.append({
                    "db_id": results['ids'][0][i],
                    "text": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    # Lower distance = higher similarity in ChromaDB's cosine space
                    "distance": results['distances'][0][i] if 'distances' in results and results['distances'] else None
                })
                
        return retrieved_clauses