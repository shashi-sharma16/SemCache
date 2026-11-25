
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.api.routes import router
from backend.services.expanded_seed_service import load_expanded_cache_seeds
from backend.services.metrics_service import initialize_metrics_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the expanded cache when the application starts."""

    initialize_metrics_db()
    load_expanded_cache_seeds()
    yield


app = FastAPI(
    title="SemCache API",
    description="An intelligent semantic caching engine for LLM applications.",
    version="1.0.0",
    lifespan=lifespan
)


app.include_router(router)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "SemCache"
    }
