import csv
import json
import time
import urllib.request
from pathlib import Path

API_URL = "http://127.0.0.1:8000/query"
METRICS_URL = "http://127.0.0.1:8000/metrics"

# 25 topics, with 4 differently worded questions per topic.
QUESTION_GROUPS = [
    [
        "What is photosynthesis and how does it work?",
        "Can you explain how photosynthesis works?",
        "How do plants use photosynthesis to make food?",
        "What happens during the process of photosynthesis?",
    ],
    [
        "What is DNS and what does it do?",
        "Explain how the Domain Name System works.",
        "How does DNS translate website names into IP addresses?",
        "What is the purpose of DNS on the internet?",
    ],
    [
        "What is recursion in programming?",
        "Explain how recursive functions work.",
        "What does recursion mean in computer programming?",
        "How does a function call itself using recursion?",
    ],
    [
        "What is database normalization?",
        "Explain the purpose of normalizing a database.",
        "How does database normalization organize data?",
        "Why do we use normalization in relational databases?",
    ],
    [
        "What is encryption and how does it protect data?",
        "Explain how encryption keeps information secure.",
        "How does encrypting data prevent unauthorized access?",
        "What does encryption do to protect digital information?",
    ],
    [
        "What is Docker and why is it used?",
        "Explain what Docker does for software development.",
        "How does Docker help developers package applications?",
        "What is the purpose of using Docker containers?",
    ],
    [
        "What is a REST API?",
        "Explain how REST APIs work.",
        "What does REST mean in web API development?",
        "How do applications communicate through a REST API?",
    ],
    [
        "What is the difference between a CPU and RAM?",
        "How are CPU and RAM different in a computer?",
        "Explain the roles of the processor and memory.",
        "What does RAM do compared with the CPU?",
    ],
    [
        "What is version control in software development?",
        "Explain why developers use version control systems.",
        "How does version control track changes in code?",
        "What is the purpose of a version control system?",
    ],
    [
        "What is an artificial neural network?",
        "Explain how neural networks work.",
        "How do artificial neural networks process information?",
        "What does a neural network do in artificial intelligence?",
    ],
    [
        "What are SQL joins used for?",
        "Explain how joins combine data from SQL tables.",
        "How can I retrieve related records using SQL joins?",
        "What is the purpose of joining tables in SQL?",
    ],
    [
        "What is an operating system?",
        "Explain the main functions of an operating system.",
        "How does an operating system manage a computer?",
        "What does system software like Windows or Linux do?",
    ],
    [
        "What is binary search in programming?",
        "Explain how the binary search algorithm works.",
        "How does binary search find an item in a sorted list?",
        "What is the process used by binary search to locate data?",
    ],
    [
        "What is probability in mathematics?",
        "Explain how probability measures the chance of an event.",
        "How do we calculate the likelihood of something happening?",
        "What does probability tell us about uncertain events?",
    ],
    [
        "What is data visualization?",
        "Explain how data visualization presents information.",
        "How do charts and graphs help us understand data?",
        "What is the purpose of visualizing datasets?",
    ],
    [
        "What are browser cookies?",
        "Explain how websites use cookies.",
        "How do cookies store information in a web browser?",
        "What is the purpose of cookies when visiting websites?",
    ],
    [
        "What is a phishing attack?",
        "Explain how phishing scams trick people.",
        "How do cybercriminals use fake messages to steal information?",
        "What are phishing attacks and how do they work?",
    ],
    [
        "What is a sorting algorithm?",
        "Explain how sorting algorithms organize data.",
        "How do computers arrange values using sorting methods?",
        "What is the purpose of sorting algorithms in programming?",
    ],
    [
        "How do solar panels generate electricity?",
        "Explain how solar energy is converted into electrical power.",
        "How does a photovoltaic panel produce electricity from sunlight?",
        "What happens when sunlight reaches a solar panel?",
    ],
    [
        "What is blockchain technology?",
        "Explain how a blockchain stores information.",
        "How does blockchain maintain a shared digital record?",
        "What makes blockchain a distributed ledger system?",
    ],
    [
        "What is a pivot table in a spreadsheet?",
        "Explain how pivot tables summarize spreadsheet data.",
        "How can a pivot table organize and analyze data?",
        "What is the purpose of creating a pivot table in Excel?",
    ],
    [
        "What is regression analysis in statistics?",
        "Explain how regression analysis identifies relationships.",
        "How can regression be used to predict numerical values?",
        "What does a regression model tell us about variables?",
    ],
    [
        "What is browser caching?",
        "Explain how web browser caching works.",
        "How does a browser save website resources for later?",
        "Why can cached website files make pages load faster?",
    ],
    [
        "What is load balancing in computer networks?",
        "Explain how a load balancer distributes traffic.",
        "How do servers share incoming requests using load balancing?",
        "What is the purpose of distributing network traffic across servers?",
    ],
    [
        "What is password hashing?",
        "Explain how password hashing protects user passwords.",
        "Why do applications store password hashes instead of plain text?",
        "How does hashing help secure passwords in a database?",
    ],
]

OUTPUT_FILE = Path(__file__).with_name("benchmark_results.csv")


def send_query(query):
    payload = json.dumps({"query": query}).encode("utf-8")
    request = urllib.request.Request(
        API_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    start = time.perf_counter()

    with urllib.request.urlopen(request, timeout=600) as response:
        result = json.loads(response.read().decode("utf-8"))

    elapsed = time.perf_counter() - start
    result["client_latency_seconds"] = round(elapsed, 6)
    return result


def get_metrics():
    request = urllib.request.Request(METRICS_URL)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))



def main():
    questions = [
        question
        for group in QUESTION_GROUPS
        for question in group
    ]

    if len(questions) != 100:
        raise ValueError(f"Expected 100 questions, found {len(questions)}")

    # Identify questions already saved in the CSV.
    completed_ids = set()

    if OUTPUT_FILE.exists():
        with OUTPUT_FILE.open(
            "r", newline="", encoding="utf-8-sig"
        ) as existing_file:
            reader = csv.DictReader(existing_file)
            completed_ids = {
                row["query_id"] for row in reader
            }

    print(f"Total questions: 100")
    print(f"Already completed: {len(completed_ids)}")
    print(f"Remaining: {100 - len(completed_ids)}")
    print()

    columns = [
        "query_id",
        "question",
        "decision",
        "cache_hit",
        "llm_called",
        "similarity",
        "latency_seconds",
        "client_latency_seconds",
        "prompt_tokens",
        "completion_tokens",
        "matched_query",
    ]

    file_mode = "a" if OUTPUT_FILE.exists() else "w"

    with OUTPUT_FILE.open(
        file_mode, newline="", encoding="utf-8-sig"
    ) as file:
        writer = csv.DictWriter(file, fieldnames=columns)

        if file_mode == "w":
            writer.writeheader()

        for index, question in enumerate(questions, start=1):
            query_id = f"Q{index:03d}"

            if query_id in completed_ids:
                continue

            try:
                print(f"Processing {query_id}...")
                result = send_query(question)

                row = {
                    "query_id": query_id,
                    "question": question,
                    "decision": result.get("decision"),
                    "cache_hit": result.get("cache_hit"),
                    "llm_called": result.get("llm_called"),
                    "similarity": result.get("similarity", ""),
                    "latency_seconds": result.get("latency_seconds", ""),
                    "client_latency_seconds": result.get(
                        "client_latency_seconds", ""
                    ),
                    "prompt_tokens": result.get("prompt_tokens", 0),
                    "completion_tokens": result.get("completion_tokens", 0),
                    "matched_query": result.get("matched_query", ""),
                }

                writer.writerow(row)
                file.flush()
                completed_ids.add(query_id)

                print(f"Saved {query_id}: {result.get('decision')}")

            except Exception as error:
                print(f"\nRequest failed at {query_id}: {error}")
                print("Completed results are safely saved.")
                print("Run the script again to resume.")
                break

    # Calculate results from the complete CSV.
    with OUTPUT_FILE.open(
        "r", newline="", encoding="utf-8-sig"
    ) as file:
        all_results = list(csv.DictReader(file))

    total = len(all_results)
    hits = sum(
        row["cache_hit"].lower() == "true"
        for row in all_results
    )
    misses = total - hits
    llm_calls = sum(
        row["llm_called"].lower() == "true"
        for row in all_results
    )

    print("\n========== BENCHMARK PROGRESS ==========")
    print(f"Questions saved:       {total}/100")
    print(f"Cache hits:            {hits}")
    print(f"Cache misses:          {misses}")
    print(f"Cache hit rate:        {hits / total * 100:.2f}%")
    print(f"LLM calls:             {llm_calls}")
    print(f"LLM calls avoided:     {hits}")

    if total == 100:
        print("\n100-QUESTION BENCHMARK COMPLETED!")

    try:
        metrics = get_metrics()
        print("\n========== API METRICS ==========")
        for key, value in metrics.items():
            print(f"{key}: {value}")
    except Exception as error:
        print(f"\nCould not retrieve API metrics: {error}")

    print(f"\nResults saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
