from functools import lru_cache
from sentence_transformers import SentenceTransformer

from backend.core.config import EMBEDDING_MODEL


@lru_cache(maxsize=1)
def get_embedding_model():
    """Load the embedding model only once."""
    return SentenceTransformer(EMBEDDING_MODEL)


def generate_embedding(text: str) -> list[float]:
    """Convert text into a normalized numerical vector."""

    model = get_embedding_model()

    embedding = model.encode(
        text,
        normalize_embeddings=True
    )

    return embedding.tolist()