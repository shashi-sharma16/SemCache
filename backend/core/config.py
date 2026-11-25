from pathlib import Path

# Project root directory
BASE_DIR = Path(__file__).resolve().parents[2]

# Embedding model
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Local LLM configuration
LLM_MODEL = "qwen2.5:3b"

# ChromaDB configuration
CHROMA_DB_PATH = BASE_DIR / "chroma_db"
COLLECTION_NAME = "semcache"

# Metrics database configuration
METRICS_DB_PATH = BASE_DIR / "data" / "metrics.db"

# Cache configuration
SIMILARITY_THRESHOLD = 0.85