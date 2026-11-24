
import csv
from pathlib import Path

from backend.services.embedding_service import generate_embedding


BASE_DIR = Path(__file__).resolve().parents[1]
BENCHMARK_FILE = BASE_DIR / "evaluation" / "benchmark.csv"

THRESHOLD = 0.40

# Three descriptions per policy.
# All descriptions are derived from the existing ShopEase policies.
POLICY_DESCRIPTIONS = {
    "ORDER_TRACKING": [
        "General order tracking",
        "Viewing shipment tracking information",
        "Checking delivery progress for an order"
    ],
    "REFUND_ELIGIBILITY": [
        "Refund eligibility",
        "Conditions for qualifying for a refund",
        "Rules determining whether a purchase qualifies for reimbursement"
    ],
    "REFUND_TIMELINE": [
        "Refund processing time",
        "Time required for an approved refund to arrive",
        "Expected refund payment processing period"
    ],
    "CANCEL_ORDER": [
        "Order cancellation",
        "Rules for cancelling an order before dispatch",
        "Cancellation availability before an order is dispatched"
    ],
    "CHANGE_ADDRESS": [
        "Changing an existing shipping address",
        "Editing the delivery address of an existing order",
        "Modifying an order's address before dispatch"
    ],
    "ADD_ADDRESS": [
        "Adding a new shipping address",
        "Saving an additional address to an account",
        "Adding a new delivery destination to a profile"
    ]
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

    # Generate all description embeddings once.
    description_embeddings = {}

    for policy_id, descriptions in POLICY_DESCRIPTIONS.items():
        description_embeddings[policy_id] = [
            generate_embedding(description)
            for description in descriptions
        ]

    correct = 0
    unidentified = 0
    mismatches = []

    for row in test_rows:
        query_embedding = generate_embedding(row["query"])

        policy_scores = {}

        for policy_id, embeddings in description_embeddings.items():
            similarities = [
                cosine_similarity(query_embedding, embedding)
                for embedding in embeddings
            ]

            # Use the highest similarity among the descriptions.
            policy_scores[policy_id] = max(similarities)

        best_policy = max(policy_scores, key=policy_scores.get)
        best_similarity = policy_scores[best_policy]

        actual = (
            best_policy
            if best_similarity >= THRESHOLD
            else None
        )

        expected = row["expected_policy_id"]

        if actual == expected:
            correct += 1
        else:
            if actual is None:
                unidentified += 1

            mismatches.append({
                "id": row["query_id"],
                "query": row["query"],
                "expected": expected,
                "actual": actual,
                "similarity": best_similarity
            })

    total = len(test_rows)
    accuracy = correct / total * 100 if total else 0

    print("\nMULTI-DESCRIPTION CLASSIFIER EXPERIMENT")
    print("=" * 55)
    print(f"Development queries : {total}")
    print(f"Threshold           : {THRESHOLD}")
    print(f"Correct policies    : {correct}")
    print(f"Incorrect           : {total - correct}")
    print(f"Unidentified        : {unidentified}")
    print(f"Accuracy            : {accuracy:.2f}%")

    print("\nMISCLASSIFICATIONS")
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


if __name__ == "__main__":
    main()
