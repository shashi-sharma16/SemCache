# SemCache

**A General-Purpose Semantic Caching Engine for LLM Applications**

SemCache is a local semantic caching system that reduces unnecessary Large Language Model (LLM) calls by recognizing questions with similar meanings and reusing previously generated answers.

Instead of generating a new response for every request, SemCache converts questions into vector embeddings and searches for semantically similar questions in a persistent ChromaDB collection.

If a sufficiently similar question already exists, its cached answer is returned without calling the LLM. Otherwise, SemCache generates a new answer using a locally running LLM and stores it for future reuse.

## How It Works

1. A user submits a question through the API.
2. SemCache converts the question into an embedding using Sentence Transformers.
3. ChromaDB searches for a semantically similar cached question.
4. If similarity meets the configured threshold, the stored answer is returned.
5. If no suitable match exists, Ollama generates a new answer.
6. The new question and answer are stored in the cache.

## Technology Stack

| Component | Technology |
|---|---|
| Backend API | FastAPI |
| Programming Language | Python |
| Embeddings | all-MiniLM-L6-v2 |
| Vector Database | ChromaDB |
| Local LLM | Qwen 2.5 3B |
| LLM Runtime | Ollama |
| Metrics Storage | SQLite |

## Project Structure

```text
SemCache/
├── backend/
│   ├── api/
│   │   └── routes.py
│   ├── core/
│   │   └── config.py
│   ├── services/
│   │   ├── cache_service.py
│   │   ├── embedding_service.py
│   │   ├── llm_service.py
│   │   ├── metrics_service.py
│   │   └── vector_store.py
│   └── main.py
├── evaluation/
│   ├── run_benchmark.py
│   └── benchmark_results.csv
├── .gitignore
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.13
- Ollama
- Git

## Installation and Setup

**1. Clone the repository**

```bash
git clone https://github.com/shashi-sharma16/SemCache.git
cd SemCache
```

**2. Create and activate a virtual environment**

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**3. Install dependencies**

```powershell
pip install -r requirements.txt
```

**4. Download the required Ollama model**

```bash
ollama pull qwen2.5:3b
```

Ensure Ollama is running before starting the application.

**5. Start the FastAPI server**

```bash
uvicorn backend.main:app --reload
```

The API will be available at:

`http://127.0.0.1:8000`

Interactive API documentation:

`http://127.0.0.1:8000/docs`

## API Usage

### POST /query

Submit a question for semantic cache lookup or LLM generation.

**Example request:**

```json
{
  "query": "What is machine learning?"
}
```

**Example cache miss response:**

```json
{
  "decision": "CACHE_MISS",
  "reason": "EMPTY_CACHE",
  "answer": "Machine learning is a branch of artificial intelligence...",
  "cache_hit": false,
  "llm_called": true,
  "prompt_tokens": 50,
  "completion_tokens": 100,
  "matched_query": null,
  "similarity": null,
  "latency_seconds": 2.5
}
```

**Example cache hit response:**

```json
{
  "decision": "CACHE_HIT",
  "reason": "SEMANTIC_MATCH_FOUND",
  "answer": "Machine learning is a branch of artificial intelligence...",
  "cache_hit": true,
  "llm_called": false,
  "matched_query": "What is machine learning?",
  "similarity": 0.93,
  "latency_seconds": 0.03
}
```

*Response values above are illustrative.*

### GET /metrics

Returns overall cache performance metrics.

The metrics include:

- Total requests
- Cache hits and misses
- Cache hit rate
- Total LLM calls
- LLM calls avoided
- Prompt and completion token usage
- Average cache-hit latency
- Average cache-miss latency

Example:

`http://127.0.0.1:8000/metrics`

## Configuration

Project settings are available in `backend/core/config.py`.

| Setting | Value |
|---|---|
| Embedding model | all-MiniLM-L6-v2 |
| LLM model | qwen2.5:3b |
| Similarity threshold | 0.85 |
| Vector database | ChromaDB |
| Metrics database | SQLite |

The similarity threshold determines how similar a new question must be to an existing cached question before its answer can be reused.

## Performance Measurement

SemCache records request-level metrics to evaluate its effectiveness.

The primary measurement is the number of requests answered directly from the semantic cache instead of calling the LLM.

**Cache hit rate:**

Cache Hit Rate = (Cache Hits / Total Requests) × 100

**LLM calls avoided:**

Every successful cache hit represents one avoided LLM invocation.

### 100-Question Benchmark Results

The system was evaluated using 100 questions arranged into 25 groups of four semantically related questions. The benchmark measures whether differently worded questions can reuse previously cached answers.

| Metric | Result |
|---|---:|
| Total questions | 100 |
| Cache hits | 21 |
| Cache misses | 79 |
| Cache hit rate | 21% |
| LLM calls | 79 |
| LLM calls avoided | 21 |
| Average cache-hit latency | 0.0218 seconds |
| Average cache-miss latency | 16.3925 seconds |
| Total prompt tokens | 4,474 |
| Total completion tokens | 13,222 |

The benchmark uses a curated set of related questions and measures semantic reuse at the configured similarity threshold of 0.85. Results may differ with other datasets, query distributions, and threshold settings.

The benchmark can be run with:

```powershell
python evaluation/run_benchmark.py
```

The script saves individual query results in `evaluation/benchmark_results.csv`.

## Important Notes

- SemCache runs locally using Ollama.
- No paid LLM API is required.
- ChromaDB stores cached question embeddings and answers persistently.
- SQLite stores request-level performance metrics.
- Cache hits reuse stored answers without making another LLM call.
- Cache misses generate a new answer and add it to the cache.
- Runtime databases and virtual environments are excluded from Git.

