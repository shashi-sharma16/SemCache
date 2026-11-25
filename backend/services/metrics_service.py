import sqlite3

from backend.core.config import METRICS_DB_PATH


def initialize_metrics_db():
    """Create the metrics database and request history table."""

    METRICS_DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(METRICS_DB_PATH) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS request_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                decision TEXT NOT NULL,
                llm_called INTEGER NOT NULL,
                prompt_tokens INTEGER NOT NULL DEFAULT 0,
                completion_tokens INTEGER NOT NULL DEFAULT 0,
                latency_seconds REAL NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)


def record_request(
    decision: str,
    llm_called: bool,
    prompt_tokens: int,
    completion_tokens: int,
    latency_seconds: float
):
    """Save the metrics of one successfully processed API request."""

    with sqlite3.connect(METRICS_DB_PATH) as connection:
        connection.execute(
            """
            INSERT INTO request_metrics (
                decision,
                llm_called,
                prompt_tokens,
                completion_tokens,
                latency_seconds
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                decision,
                int(llm_called),
                prompt_tokens,
                completion_tokens,
                latency_seconds
            )
        )

def get_metrics():
    """Calculate overall semantic cache performance metrics."""

    with sqlite3.connect(METRICS_DB_PATH) as connection:
        connection.row_factory = sqlite3.Row

        result = connection.execute("""
            SELECT
                COUNT(*) AS total_requests,

                SUM(CASE WHEN decision = 'CACHE_HIT'
                    THEN 1 ELSE 0 END) AS cache_hits,

                SUM(CASE WHEN decision = 'CACHE_MISS'
                    THEN 1 ELSE 0 END) AS cache_misses,

                SUM(llm_called) AS total_llm_calls,

                SUM(CASE WHEN decision = 'CACHE_HIT'
                    THEN 1 ELSE 0 END) AS llm_calls_avoided,

                SUM(prompt_tokens) AS total_prompt_tokens,

                SUM(completion_tokens) AS total_completion_tokens,

                AVG(CASE WHEN decision = 'CACHE_HIT'
                    THEN latency_seconds END) AS avg_hit_latency,

                AVG(CASE WHEN decision = 'CACHE_MISS'
                    THEN latency_seconds END) AS avg_miss_latency

            FROM request_metrics
        """).fetchone()

    total = result["total_requests"] or 0
    hits = result["cache_hits"] or 0

    return {
        "total_requests": total,
        "cache_hits": hits,
        "cache_misses": result["cache_misses"] or 0,
        "cache_hit_rate_percent": round(
            (hits / total) * 100, 2
        ) if total else 0,
        "total_llm_calls": result["total_llm_calls"] or 0,
        "llm_calls_avoided": result["llm_calls_avoided"] or 0,
        "total_prompt_tokens": result["total_prompt_tokens"] or 0,
        "total_completion_tokens": result["total_completion_tokens"] or 0,
        "avg_hit_latency_seconds": round(
            result["avg_hit_latency"], 6
        ) if result["avg_hit_latency"] is not None else 0,
        "avg_miss_latency_seconds": round(
            result["avg_miss_latency"], 6
        ) if result["avg_miss_latency"] is not None else 0
    }