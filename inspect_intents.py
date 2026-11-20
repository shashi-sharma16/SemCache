
import csv
import re

file_path = "dataset/raw/bitext_customer_support.csv"

selected_intents = [
    "track_order",
    "track_refund",
    "cancel_order",
    "check_refund_policy",
    "change_shipping_address",
    "set_up_shipping_address",
    "payment_issue",
    "recover_password"
]

with open(file_path, "r", encoding="utf-8", newline="") as file:
    rows = list(csv.DictReader(file))

print("REPRESENTATIVE QUESTIONS BY INTENT")

for intent in selected_intents:
    matching_rows = [
        row for row in rows if row["intent"] == intent
    ]

    print(f"\n{'=' * 55}")
    print(f"INTENT: {intent}")
    print(f"Total records: {len(matching_rows)}")

    for row in matching_rows[:3]:
        print("\nQuestion:", row["instruction"])
        print("Response:", row["response"][:250], "...")

print("\nPLACEHOLDER ANALYSIS")

placeholders = set()

for row in rows:
    found = re.findall(
        r"\{\{.*?\}\}",
        row["instruction"] + " " + row["response"]
    )
    placeholders.update(found)

print("Unique placeholders found:", len(placeholders))

for placeholder in sorted(placeholders):
    print(placeholder)
