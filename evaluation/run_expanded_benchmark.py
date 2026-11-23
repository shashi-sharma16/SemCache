
import csv
from pathlib import Path

from backend.services.query_guard import guard_query
from backend.services.policy_classifier import identify_policy
from backend.services.cache_service import lookup_expanded_cache


BASE_DIR = Path(__file__).resolve().parents[1]
BENCHMARK_FILE = BASE_DIR / "evaluation" / "benchmark.csv"
RESULT_FILE = BASE_DIR / "evaluation" / "expanded_benchmark_results.csv"

THRESHOLDS = [0.75, 0.80, 0.85, 0.90, 0.95]


def run_benchmark():
    with open(BENCHMARK_FILE, "r", encoding="utf-8", newline="") as file:
        queries = list(csv.DictReader(file))

    results = []

    for query in queries:
        text = query["query"]

        # Stage 1: Query Guard
        guard_result = guard_query(text)
        decision = guard_result["decision"]

        # Stage 2: Policy identification and expanded cache lookup
        policy_result = None
        match = {"cache_hit": False}

        if decision == "CACHE_LOOKUP":
            policy_result = identify_policy(text)

            if policy_result["identified"]:
                match = lookup_expanded_cache(
                    query=text,
                    policy_id=policy_result["policy_id"],
                    threshold=0.0
                )

        for threshold in THRESHOLDS:
            predicted_hit = (
                match["cache_hit"]
                and match["similarity"] >= threshold
            )

            correct_hit = (
                predicted_hit
                and query["expected_outcome"] == "CACHE_LOOKUP"
                and match["policy_id"] == query["expected_policy_id"]
            )

            false_hit = predicted_hit and not correct_hit

            missed_opportunity = (
                query["expected_outcome"] == "CACHE_LOOKUP"
                and not correct_hit
            )

            results.append({
                "query_id": query["query_id"],
                "threshold": threshold,
                "guard_decision": decision,
                "identified_policy_id": (
                    policy_result["policy_id"]
                    if policy_result and policy_result["identified"]
                    else ""
                ),
                "policy_similarity": (
                    policy_result["similarity"]
                    if policy_result
                    else ""
                ),
                "expected_outcome": query["expected_outcome"],
                "expected_policy_id": query["expected_policy_id"],
                "matched_policy_id": match.get("policy_id", ""),
                "similarity": match.get("similarity", ""),
                "predicted_hit": predicted_hit,
                "correct_hit": correct_hit,
                "false_hit": false_hit,
                "missed_opportunity": missed_opportunity
            })

    with open(RESULT_FILE, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=results[0].keys()
        )
        writer.writeheader()
        writer.writerows(results)

    print("Benchmark queries:", len(queries))
    print("Thresholds tested:", len(THRESHOLDS))
    print("Total evaluation records:", len(results))
    print("Results saved to:", RESULT_FILE)


if __name__ == "__main__":
    run_benchmark()
