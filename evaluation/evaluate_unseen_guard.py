
import csv
from pathlib import Path
from collections import Counter

from backend.services.query_guard import guard_query


BASE_DIR = Path(__file__).resolve().parents[1]
TEST_FILE = BASE_DIR / "evaluation" / "unseen_test.csv"


def main():
    with open(TEST_FILE, encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))

    correct = 0
    confusion = Counter()
    mismatches = []

    for row in rows:
        query_id = row["query_id"]
        query = row["query"]
        expected = row["expected_outcome"]

        result = guard_query(query)
        actual = result["decision"]

        confusion[(expected, actual)] += 1

        if expected == actual:
            correct += 1
        else:
            mismatches.append({
                "id": query_id,
                "query": query,
                "expected": expected,
                "actual": actual,
                "reason": result["reason"]
            })

    total = len(rows)
    accuracy = correct / total * 100 if total else 0

    print("\nUNSEEN QUERY GUARD EVALUATION")
    print("=" * 55)
    print(f"Total queries : {total}")
    print(f"Correct       : {correct}")
    print(f"Incorrect     : {total - correct}")
    print(f"Accuracy      : {accuracy:.2f}%")

    print("\nCONFUSION COUNTS")
    print("-" * 55)

    for (expected, actual), count in sorted(confusion.items()):
        print(f"Expected: {expected:<18} Actual: {actual:<18} Count: {count}")

    print("\nMISCLASSIFIED QUERIES")
    print("-" * 55)

    if not mismatches:
        print("No misclassifications!")
    else:
        for item in mismatches:
            print(f"\n{item['id']}")
            print(f"Query    : {item['query']}")
            print(f"Expected : {item['expected']}")
            print(f"Actual   : {item['actual']}")
            print(f"Reason   : {item['reason']}")


if __name__ == "__main__":
    main()
