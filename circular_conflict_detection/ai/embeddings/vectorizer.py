from typing import List
try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    raise ImportError("Please install sentence-transformers (pip install sentence-transformers)")


class EmbeddingService:
    """
    Generates vector embeddings for Persian text chunks using Sentence-Transformers.
    """
    def __init__(self, model_name: str = "sentence-transformers/LaBSE"):
        # LaBSE is highly optimized for cross-lingual and Persian semantic search.
        # It downloads the model weights on the first run.
        self.model = SentenceTransformer(model_name)

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Converts a list of text chunks into dense vector embeddings.
        
        Args:
            texts (List[str]): The Persian clauses to embed.
            
        Returns:
            List[List[float]]: A list of embedding vectors.
        """
        if not texts:
            return []
            
        # show_progress_bar=False prevents logging noise in your backend console
        embeddings = self.model.encode(texts, show_progress_bar=False)
        
        # Convert numpy arrays to standard Python lists for ChromaDB compatibility
        return embeddings.tolist()