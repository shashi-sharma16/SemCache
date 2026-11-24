# SemCache

**An Intelligent Semantic Caching Engine for LLM Applications**

SemCache is a local semantic caching engine designed to reduce repeated Large Language Model (LLM) calls by identifying semantically similar queries and reusing previously stored responses.

Unlike basic similarity-based caching, SemCache combines query routing, policy classification, and policy-aware semantic retrieval to reduce the risk of returning an irrelevant or incorrect cached answer.

## Problem Statement

LLM applications often receive repeated questions expressed in different ways. Generating a new response for every repeated query increases inference workload and response latency.

However, blindly reusing responses based only on text similarity can produce incorrect results, particularly when a question requires customer-specific or live information.

SemCache addresses this problem through a multi-stage query-processing pipeline.

## Architecture

A customer query passes through the following stages:

1. **Query Guard:** Determines whether the request should use the cache, bypass it, request clarification, or require review.
2. **Policy Classifier:** Identifies the relevant supported policy for cacheable queries.
3. **Semantic Cache:** Searches for a sufficiently similar query within the identified policy.
4. **Policy-Based Fallback:** If no sufficiently similar cached response exists, SemCache returns the authoritative answer from its policy knowledge base.

### Request Flow

```text
Customer Query
      |
      v
  Query Guard
      |
      +---- CLARIFY
      |
      +---- REVIEW_REQUIRED
      |
      +---- BYPASS_CACHE
      |
      v
 Policy Classifier
      |
      +---- Policy Not Identified
      |          |
      |          v
      |     REVIEW_REQUIRED
      |
      v
 Policy-Aware Semantic Cache
      |
      +---- Cache Hit
      |        |
      |        v
      |   Return Cached Answer
      |
      +---- Cache Miss
               |
               v
         Retrieve Policy Answer
               |
               v
         Return Policy Answer
```

## Key Features

- Semantic similarity-based query matching.
- Policy-aware cache retrieval.
- Query Guard for request routing.
- Policy classification using sentence embeddings.
- Authoritative policy-based responses on cache misses.
- Local LLM service available for future verified-generation improvements.
- Customer-specific request bypass.
- Clarification and unsupported-request handling.
- REST API built with FastAPI.
- Persistent vector storage using ChromaDB.
- Benchmarking and manually curated unseen-query evaluation.

## Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| API Framework | FastAPI |
| API Server | Uvicorn |
| Embedding Model | all-MiniLM-L6-v2 |
| Vector Database | ChromaDB |
| Local LLM Runtime | Ollama |
| LLM | Qwen 2.5 3B |
| Data Validation | Pydantic |
| Version Control | Git and GitHub |

## Project Structure

```text
SemCache/
│
├── backend/
│   ├── api/
│   │   └── routes.py
│   │
│   ├── core/
│   │   └── config.py
│   │
│   ├── services/
│   │   ├── cache_service.py
│   │   ├── embedding_service.py
│   │   ├── expanded_seed_service.py
│   │   ├── llm_service.py
│   │   ├── policy_classifier.py
│   │   ├── policy_service.py
│   │   ├── query_guard.py
│   │   ├── seed_service.py
│   │   └── vector_store.py
│   │
│   └── main.py
│
├── dataset/
│   ├── raw/
│   ├── bitext_selected_60.csv
│   ├── query_policy_mapping.csv
│   └── shopease_policies.json
│
├── evaluation/
│   ├── benchmark.csv
│   ├── cache_seeds.csv
│   ├── expanded_cache_seeds.csv
│   ├── unseen_test.csv
│   └── evaluation scripts and reports
│
├── requirements.txt
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.13
- Ollama
- Git

### 1. Clone the repository

```bash
git clone https://github.com/shashi-sharma16/SemCache.git
cd SemCache
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up Ollama

Install Ollama separately, then download the model:

```bash
ollama pull qwen2.5:3b
```

Ensure the Ollama service is running.

### 5. Start the API

From the project root:

```bash
uvicorn backend.main:app --reload
```

The API will be available at:

`http://127.0.0.1:8000`

Swagger documentation:

`http://127.0.0.1:8000/docs`

Health endpoint:

`http://127.0.0.1:8000/health`

The expanded semantic cache is initialized automatically when the application starts.

## API Usage

### POST /query

Request:

```json
{
  "query": "How do I track my order?"
}
```

Example response:

```json
{
  "decision": "CACHE_LOOKUP",
  "reason": "SEMANTIC_CACHE_HIT",
  "answer": "To track your order, log in to your ShopEase account...",
  "cache_hit": true,
  "policy_id": "ORDER_TRACKING",
  "similarity": 0.9999,
  "matched_query": "How do I track my order?"
}
```

### GET /health

Checks whether the API is operational.

## Evaluation

SemCache was evaluated using a curated customer-support benchmark and a separate manually curated unseen-query holdout.

### Expanded Cache Benchmark

The expanded cache contains 14 seed entries, compared with 6 entries in the original cache.

| Similarity Threshold | Original Cache Recall | Expanded Cache Recall |
|---|---:|---:|
| 0.75 | 47.6% | 59.5% |
| 0.80 | 33.3% | 47.6% |
| 0.85 | 26.2% | 38.1% |
| 0.90 | 9.5% | 19.0% |
| 0.95 | 2.4% | 9.5% |

At a threshold of 0.75, the expanded cache recovered five additional correct matches compared with the original cache, with no false cache hits on this benchmark.

### API Performance Benchmark

The API was evaluated using 100 customer-support queries before and after replacing LLM-generated cache-miss responses with authoritative policy-based responses.

| Metric | Before Policy Fallback | Current Policy Fallback |
|---|---:|---:|
| Requests | 100 | 100 |
| Successful Requests | 100 | 100 |
| Mean Latency | 1.3729 s | 0.0737 s |
| Median Latency | 0.0172 s | 0.0224 s |
| P95 Latency | 6.3420 s | 0.1328 s |
| Maximum Latency | 11.2778 s | 2.4650 s |

**Key Observations:**

- Mean API latency decreased by approximately 94.6%.
- P95 latency decreased by approximately 97.9%.
- Maximum observed latency decreased from 11.2778 seconds to 2.465 seconds.
- Both implementations successfully processed all 100 requests.

The improvement primarily reflects the removal of local LLM generation from the cache-miss response path. The current implementation retrieves authoritative policy answers instead.

These are observed results from sequential tests on the same local machine, not controlled production-scale benchmarks. The median latency increased slightly, indicating that the improvement was concentrated in requests that previously incurred expensive LLM generation.

### Unseen-Query Evaluation

| Component | Evaluation Result |
|---|---:|
| Query Guard | 84% accuracy |
| Policy Classifier | 88% accuracy |
| Expanded Cache at 0.75 | 87.5% precision |
| Expanded Cache at 0.75 | 28% recall |

The unseen cache evaluation recorded seven correct hits and one false hit at the 0.75 threshold.

### Important Evaluation Limitations

- The datasets are curated and do not represent real customer-support traffic.
- The ShopEase company and its policies are fictional.
- Benchmark results depend on the selected cache seeds and similarity thresholds.
- Some development thresholds were selected using the development benchmark.
- The unseen-query holdout is manually curated, not independently collected external data.
- The Query Guard is a rule-based prototype and should not be treated as a production safety guarantee.

## Current Limitations

- No integration with a real customer-support or order-management system.
- Customer-specific requests are directed to support rather than retrieved from live customer records.
- The API currently returns authoritative policy answers on cache misses rather than unverified LLM-generated responses.
- LLM-generated responses are not automatically added to the cache.
- The current policy classifier supports a limited set of predefined policies.
- Production-scale performance and latency testing remain future work.

## Future Improvements

- Improve policy classification on unseen queries.
- Introduce more robust query-routing techniques.
- Evaluate adaptive similarity thresholds.
- Add cache monitoring and performance metrics.
- Explore controlled cache updates and invalidation.
- Integrate with external LLM applications through a reusable API.

## Project Status

**Core API integration and initial end-to-end testing completed.**

SemCache is an experimental portfolio project exploring semantic caching, policy-aware retrieval, and safe query routing for LLM applications.

