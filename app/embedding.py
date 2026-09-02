"""
embedding.py

Handles:
1. Loading SentenceTransformer model
2. Generating embeddings
3. Batch embedding generation
"""

from typing import List

from sentence_transformers import SentenceTransformer


class EmbeddingModel:
    """
    Wrapper class around SentenceTransformer.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Load model only once.
        """

        print(f"Loading model: {model_name}")

        self.model = SentenceTransformer(model_name)

        print("Model loaded successfully.")

    def generate_embedding(self, text: str):
        """
        Generate embedding for a single text.
        """

        if not text:
            return None

        embedding = self.model.encode(
            text,
            convert_to_numpy=True
        )

        return embedding

    def generate_embeddings(
        self,
        texts: List[str]
    ):
        """
        Generate embeddings for multiple texts.
        """

        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            batch_size=32,
            show_progress_bar=False
        )

        return embeddings


# Singleton model instance
embedding_model = EmbeddingModel()