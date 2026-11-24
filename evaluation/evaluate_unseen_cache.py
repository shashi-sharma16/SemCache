
import csv
import sys 
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from backend.services.query_guard import guard_query
from backend.services.policy_classifier import identify_policy
from backend.services.cache_service import lookup_expanded_cache

TEST_FILE = BASE_DIR / "evaluation" / "unseen_test.csv"
RESULT_FILE = BASE_DIR / "evaluation" / "unseen_cache_results.csv"

THRESHOLDS = [0.75, 0.80, 0.85, 0.90, 0.95]


def run_evaluation():

    with open(TEST_FILE, encoding="utf-8-sig", newline="") as file:
        queries = list(csv.DictReader(file))

    results = []

    for query in queries:

        text = query["query"]

        expected_outcome = query["expected_outcome"]
        expected_policy = query["expected_policy_id"]

        # Stage 1: Query Guard
        guard_result = guard_query(text)
        decision = guard_result["decision"]

        policy_result = None
        match = {"cache_hit": False}

        # Stage 2: Policy Classification
        if decision == "CACHE_LOOKUP":

            policy_result = identify_policy(text)

            # Stage 3: Expanded Cache Lookup
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
                and expected_outcome == "CACHE_LOOKUP"
                and match["policy_id"] == expected_policy
            )

            false_hit = predicted_hit and not correct_hit

            missed_opportunity = (
                expected_outcome == "CACHE_LOOKUP"
                and not correct_hit
            )

            results.append({
                "query_id": query["query_id"],
                "threshold": threshold,
                "expected_outcome": expected_outcome,
                "guard_decision": decision,
                "guard_correct": decision == expected_outcome,
                "expected_policy_id": expected_policy,
                "identified_policy_id": (
                    policy_result["policy_id"]
                    if policy_result and policy_result["identified"]
                    else ""
                ),
                "classifier_correct": (
                    policy_result["identified"]
                    and policy_result["policy_id"] == expected_policy
                    if policy_result and expected_outcome == "CACHE_LOOKUP"
                    else ""
                ),
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

    print("\nUNSEEN END-TO-END CACHE EVALUATION")
    print("=" * 55)
    print("Unseen queries:", len(queries))
    print("Thresholds tested:", len(THRESHOLDS))
    print("Total evaluation records:", len(results))
    print("Results saved to:", RESULT_FILE)


if __name__ == "__main__":
    run_evaluation()
