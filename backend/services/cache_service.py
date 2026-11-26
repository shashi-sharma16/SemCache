import uuid

from backend.core.config import SIMILARITY_THRESHOLD
from backend.services.embedding_service import generate_embedding
from backend.services.vector_store import (
    search_general_cache,
    add_general_cache_entry
)


def lookup_general_cache(
    query: str,
    threshold: float = SIMILARITY_THRESHOLD
):
    """Search for a semantically similar cached question."""

    embedding = generate_embedding(query)

    result = search_general_cache(embedding=embedding)

    if result is None:
        return {
            "cache_hit": False,
            "reason": "EMPTY_CACHE"
        }

    similarity = max(0.0, min(1.0, 1 - result["distance"]))

    if similarity >= threshold:
        return {
            "cache_hit": True,
            "answer": result["metadata"]["answer"],
            "matched_query": result["query"],
            "similarity": similarity
        }

    return {
        "cache_hit": False,
        "reason": "SIMILARITY_BELOW_THRESHOLD",
        "matched_query": result["query"],
        "similarity": similarity
    }


def store_general_cache(query: str, answer: str):
    """Store a generated question-answer pair."""

    embedding = generate_embedding(query)

    add_general_cache_entry(
        cache_id=str(uuid.uuid4()),
        query=query,
        embedding=embedding,
        answer=answer
    )