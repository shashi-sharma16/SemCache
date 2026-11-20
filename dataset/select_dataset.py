
import csv
import random
from collections import defaultdict
from pathlib import Path

# File locations
BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "raw" / "bitext_customer_support.csv"
OUTPUT_FILE = BASE_DIR / "bitext_selected_60.csv"

# Intents we want to study
TARGET_INTENTS = [
    "track_order",
    "track_refund",
    "cancel_order",
    "check_refund_policy",
    "change_shipping_address",
    "set_up_shipping_address"
]

# Number of queries to select for each intent
QUERIES_PER_INTENT = 10

# Fixed random seed makes selection reproducible
random_generator = random.Random(42)

# Store records grouped by intent
grouped_records = defaultdict(list)

# Read the original dataset
with open(INPUT_FILE, "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)

    for row_number, row in enumerate(reader, start=1):
        if row["intent"] in TARGET_INTENTS:
            row["source_row_id"] = row_number
            grouped_records[row["intent"]].append(row)

# Select diverse queries
selected_records = []

for intent in TARGET_INTENTS:
    records = grouped_records[intent]

    # Shuffle records using our fixed random seed
    random_generator.shuffle(records)

    selected = []
    used_flags = set()
    used_instructions = set()

    # First, prefer different flag combinations
    for record in records:
        instruction = record["instruction"].strip()
        flags = record["flags"]

        if instruction in used_instructions:
            continue

        if flags not in used_flags:
            selected.append(record)
            used_flags.add(flags)
            used_instructions.add(instruction)

        if len(selected) == QUERIES_PER_INTENT:
            break

    # Fill remaining slots if needed
    if len(selected) < QUERIES_PER_INTENT:
        for record in records:
            instruction = record["instruction"].strip()

            if instruction not in used_instructions:
                selected.append(record)
                used_instructions.add(instruction)

            if len(selected) == QUERIES_PER_INTENT:
                break

    if len(selected) < QUERIES_PER_INTENT:
        raise ValueError(
            f"Not enough unique queries for intent: {intent}"
        )

    selected_records.extend(selected)

# Save selected queries
fieldnames = [
    "source_row_id",
    "flags",
    "category",
    "intent",
    "instruction"
]

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()

    for record in selected_records:
        writer.writerow({
            field: record[field]
            for field in fieldnames
        })

print("Dataset selection completed!")
print(f"Total selected queries: {len(selected_records)}")

print("\nQueries selected per intent:")

for intent in TARGET_INTENTS:
    count = sum(
        1 for record in selected_records
        if record["intent"] == intent
    )
    print(f"{intent}: {count}")

print(f"\nOutput saved to: {OUTPUT_FILE}")
