
import time

from fastapi import APIRouter
from pydantic import BaseModel, Field, field_validator

from backend.services.cache_service import (
    lookup_general_cache,
    store_general_cache
)
from backend.services.llm_service import generate_answer
from backend.services.metrics_service import record_request, get_metrics


router = APIRouter()


class QueryRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Question to process using semantic caching"
    )

    @field_validator("query")
    @classmethod
    def validate_query(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Query cannot be empty or contain only whitespace.")

        return value


@router.post("/query")
def process_query(request: QueryRequest):
    query = request.query.strip()
    start_time = time.perf_counter()

    # Step 1: Search the semantic cache
    cache_result = lookup_general_cache(query)

    if cache_result["cache_hit"]:

        latency = round(time.perf_counter() - start_time, 6)

        record_request(
            decision="CACHE_HIT",
            llm_called=False,
            prompt_tokens=0,
            completion_tokens=0,
            latency_seconds=latency
        )
        return {
            "decision": "CACHE_HIT",
            "reason": "SEMANTIC_MATCH_FOUND",
            "answer": cache_result["answer"],
            "cache_hit": True,
            "llm_called": False,
            "matched_query": cache_result["matched_query"],
            "similarity": cache_result["similarity"],
            "latency_seconds": latency
        }

    # Step 2: Cache miss - generate a new answer using the LLM
    llm_result = generate_answer(query)

    answer = llm_result["answer"]
    prompt_tokens = llm_result["prompt_tokens"]
    completion_tokens = llm_result["completion_tokens"]

    # Step 3: Store the generated answer in the semantic cache
    store_general_cache(query, answer)

    latency = round(time.perf_counter() - start_time, 6)

    record_request(
        decision="CACHE_MISS",
        llm_called=True,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        latency_seconds=latency
    )

    return {
        "decision": "CACHE_MISS",
        "reason": cache_result["reason"],
        "answer": answer,
        "cache_hit": False,
        "llm_called": True,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "matched_query": cache_result.get("matched_query"),
        "similarity": cache_result.get("similarity"),
        "latency_seconds": latency
    }

@router.get("/metrics")
def read_metrics():
    """Return overall semantic cache performance metrics."""

    return get_metrics()
