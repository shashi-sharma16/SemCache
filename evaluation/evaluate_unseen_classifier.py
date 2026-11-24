
import csv
from pathlib import Path
from collections import Counter

from backend.services.policy_classifier import identify_policy


BASE_DIR = Path(__file__).resolve().parents[1]
TEST_FILE = BASE_DIR / "evaluation" / "unseen_test.csv"


def main():
    with open(TEST_FILE, encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))

    # Evaluate only queries expected to use the cache.
    test_rows = [
        row for row in rows
        if row["expected_outcome"] == "CACHE_LOOKUP"
    ]

    correct = 0
    unidentified = 0
    mismatches = []
    policy_counts = Counter()

    for row in test_rows:
        result = identify_policy(row["query"])

        expected = row["expected_policy_id"]
        actual = result["policy_id"]
        similarity = result["similarity"]

        policy_counts[(expected, actual)] += 1

        if not result["identified"]:
            unidentified += 1

        if actual == expected and result["identified"]:
            correct += 1
        else:
            mismatches.append({
                "id": row["query_id"],
                "query": row["query"],
                "expected": expected,
                "actual": actual,
                "similarity": similarity,
                "identified": result["identified"]
            })

    total = len(test_rows)
    accuracy = correct / total * 100 if total else 0

    print("\nUNSEEN POLICY CLASSIFIER EVALUATION")
    print("=" * 55)
    print(f"Cacheable queries : {total}")
    print(f"Correct policies : {correct}")
    print(f"Incorrect         : {total - correct}")
    print(f"Unidentified      : {unidentified}")
    print(f"Accuracy          : {accuracy:.2f}%")

    print("\nPOLICY PREDICTIONS")
    print("-" * 55)

    for (expected, actual), count in sorted(
        policy_counts.items(),
        key=lambda item: (item[0][0], item[0][1] or "")
    ):
        print(f"Expected: {expected:<22} Actual: {str(actual):<22} Count: {count}")

    print("\nMISCLASSIFIED QUERIES")
    print("-" * 55)

    if not mismatches:
        print("No misclassifications!")
    else:
        for item in mismatches:
            print(f"\n{item['id']}")
            print(f"Query      : {item['query']}")
            print(f"Expected   : {item['expected']}")
            print(f"Actual     : {item['actual']}")
            print(f"Similarity : {item['similarity']:.4f}")
            print(f"Identified : {item['identified']}")


if __name__ == "__main__":
    main()
