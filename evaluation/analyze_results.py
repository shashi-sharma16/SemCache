
import csv
from collections import defaultdict

RESULT_FILE = "evaluation/benchmark_results.csv"

with open(RESULT_FILE, "r", encoding="utf-8", newline="") as file:
    rows = list(csv.DictReader(file))

groups = defaultdict(list)

for row in rows:
    groups[float(row["threshold"])].append(row)

print(
    f"{'THRESHOLD':<12}"
    f"{'PREDICTED':<12}"
    f"{'CORRECT':<10}"
    f"{'FALSE':<10}"
    f"{'MISSED':<10}"
    f"{'PRECISION':<12}"
    f"{'RECALL':<10}"
)

for threshold, group in sorted(groups.items()):
    predicted = sum(r["predicted_hit"] == "True" for r in group)
    correct = sum(r["correct_hit"] == "True" for r in group)
    false = sum(r["false_hit"] == "True" for r in group)
    missed = sum(r["missed_opportunity"] == "True" for r in group)

    precision = correct / predicted if predicted else 0
    recall = correct / 42

    print(
        f"{threshold:<12.2f}"
        f"{predicted:<12}"
        f"{correct:<10}"
        f"{false:<10}"
        f"{missed:<10}"
        f"{precision:<12.3f}"
        f"{recall:<10.3f}"
    )

# Inspect false cache hits at lower thresholds
with open("evaluation/benchmark.csv", "r", encoding="utf-8") as file:
    benchmark = {
        row["query_id"]: row
        for row in csv.DictReader(file)
    }

print("\nFALSE CACHE HIT DETAILS")

for threshold in [0.75, 0.80]:
    print(f"\n--- Threshold: {threshold} ---")

    for result in groups[threshold]:
        if result["false_hit"] == "True":
            original = benchmark[result["query_id"]]

            print("Query:", original["query"])
            print("Expected outcome:", original["expected_outcome"])
            print("Expected policy:", original["expected_policy_id"])
            print("Matched policy:", result["matched_policy_id"])
            print("Similarity:", result["similarity"])
            print("-" * 50)