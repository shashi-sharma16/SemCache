
import csv
from pathlib import Path

from backend.services.embedding_service import generate_embedding
from backend.services.policy_service import load_policies


BASE_DIR = Path(__file__).resolve().parents[1]
BENCHMARK_FILE = BASE_DIR / "evaluation" / "benchmark.csv"

THRESHOLD = 0.40

CACHEABLE_POLICY_IDS = {
    "ORDER_TRACKING",
    "REFUND_ELIGIBILITY",
    "REFUND_TIMELINE",
    "CANCEL_ORDER",
    "CHANGE_ADDRESS",
    "ADD_ADDRESS"
}


def cosine_similarity(first, second):
    return sum(a * b for a, b in zip(first, second))


def main():
    with open(BENCHMARK_FILE, encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))

    test_rows = [
        row for row in rows
        if row["expected_outcome"] == "CACHE_LOOKUP"
    ]

    policies = load_policies()

    # Precompute policy embeddings for both representations.
    topic_embeddings = {}
    rich_embeddings = {}

    for policy_id in CACHEABLE_POLICY_IDS:
        policy = policies[policy_id]

        topic_embeddings[policy_id] = generate_embedding(
            policy["topic"]
        )

        rich_text = policy["topic"] + ". " + policy["answer"]

        rich_embeddings[policy_id] = generate_embedding(
            rich_text
        )

    results = {
        "TOPIC_ONLY": [],
        "TOPIC_PLUS_ANSWER": []
    }

    for row in test_rows:
        query_embedding = generate_embedding(row["query"])
        expected = row["expected_policy_id"]

        for method, embeddings in [
            ("TOPIC_ONLY", topic_embeddings),
            ("TOPIC_PLUS_ANSWER", rich_embeddings)
        ]:
            similarities = {
                policy_id: cosine_similarity(
                    query_embedding,
                    policy_embedding
                )
                for policy_id, policy_embedding in embeddings.items()
            }

            best_policy = max(similarities, key=similarities.get)
            best_similarity = similarities[best_policy]

            actual = (
                best_policy
                if best_similarity >= THRESHOLD
                else None
            )

            results[method].append({
                "query_id": row["query_id"],
                "expected": expected,
                "actual": actual,
                "similarity": best_similarity
            })

    print("\nCLASSIFIER REPRESENTATION COMPARISON")
    print("=" * 60)
    print(f"Development queries: {len(test_rows)}")
    print(f"Threshold: {THRESHOLD}")

    for method, predictions in results.items():
        correct = sum(
            item["actual"] == item["expected"]
            for item in predictions
        )

        unidentified = sum(
            item["actual"] is None
            for item in predictions
        )

        accuracy = correct / len(predictions) * 100

        print(f"\n{method}")
        print("-" * 45)
        print(f"Correct policies : {correct}")
        print(f"Unidentified     : {unidentified}")
        print(f"Accuracy         : {accuracy:.2f}%")

        print("Misclassifications:")

        for item in predictions:
            if item["actual"] != item["expected"]:
                print(
                    f"{item['query_id']} | "
                    f"Expected: {item['expected']} | "
                    f"Actual: {item['actual']} | "
                    f"Similarity: {item['similarity']:.4f}"
                )


if __name__ == "__main__":
    main()
