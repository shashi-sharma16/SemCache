import csv

# Input files
bitext_file = "evaluation/bitext_review.csv"
manual_file = "evaluation/manual_queries.csv"
output_file = "evaluation/benchmark.csv"

columns = [
    "query_id",
    "source_row_id",
    "query",
    "query_type",
    "expected_policy_id",
    "expected_outcome",
    "cacheable",
    "related_query_id",
    "source"
]

benchmark = []

# 1. Add the 60 Bitext records
with open(bitext_file, encoding="utf-8-sig", newline="") as file:
    for row in csv.DictReader(file):
        benchmark.append({
            "query_id": row["query_id"],
            "source_row_id": row["source_row_id"],
            "query": row["query"],
            "query_type": "BITEXT_QUERY",
            "expected_policy_id": row["expected_policy_id"],
            "expected_outcome": row["expected_outcome"],
            "cacheable": row["cacheable"],
            "related_query_id": "",
            "source": "bitext"
        })

# 2. Add the 40 manual records
with open(manual_file, encoding="utf-8-sig", newline="") as file:
    for row in csv.DictReader(file):
        benchmark.append({
            column: row[column]
            for column in columns
        })

# 3. Check query IDs
ids = [row["query_id"] for row in benchmark]

if len(ids) != len(set(ids)):
    raise ValueError("Duplicate query IDs found!")

if len(benchmark) != 100:
    raise ValueError(
        f"Expected 100 records, found {len(benchmark)}"
    )

# 4. Save the combined benchmark
with open(output_file, "w", encoding="utf-8", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=columns)
    writer.writeheader()
    writer.writerows(benchmark)

print("BENCHMARK CREATED")
print("------------------------------")
print("Bitext records: 60")
print("Manual records: 40")
print("Total records:", len(benchmark))
print("Unique query IDs:", len(set(ids)))
print("Output:", output_file)
