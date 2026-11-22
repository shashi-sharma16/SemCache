
import csv

# Read the selected Bitext queries
with open("dataset/bitext_selected_60.csv", encoding="utf-8-sig") as file:
    selected = list(csv.DictReader(file))

# Read the existing policy mappings
with open("dataset/query_policy_mapping.csv", encoding="utf-8-sig") as file:
    mappings = list(csv.DictReader(file))

# Match each query with its mapping using source_row_id
mapping_by_id = {
    row["source_row_id"]: row
    for row in mappings
}

review_records = []

for index, query in enumerate(selected, start=1):
    mapping = mapping_by_id[query["source_row_id"]]

    policy = mapping["expected_policy_id"]
    cacheable = mapping["cacheable"]

    if cacheable == "true":
        outcome = "CACHE_LOOKUP"
    elif policy == "NEEDS_CLARIFICATION":
        outcome = "CLARIFY"
    elif policy in ("ORDER_LIVE_STATUS", "REFUND_STATUS"):
        outcome = "BYPASS_CACHE"
    else:
        outcome = "REVIEW_REQUIRED"

    review_records.append({
        "query_id": f"B{index:03d}",
        "source_row_id": query["source_row_id"],
        "query": query["instruction"],
        "bitext_intent": query["intent"],
        "expected_policy_id": policy,
        "expected_outcome": outcome,
        "cacheable": cacheable,
        "review_status": mapping["review_status"]
    })

# Save the consolidated review table
with open(
    "evaluation/bitext_review.csv",
    "w",
    newline="",
    encoding="utf-8"
) as file:
    writer = csv.DictWriter(
        file,
        fieldnames=review_records[0].keys()
    )
    writer.writeheader()
    writer.writerows(review_records)

print("Bitext review table created successfully!")
print("Total records:", len(review_records))
print("Output: evaluation/bitext_review.csv")
