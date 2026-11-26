from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.api.routes import router
from backend.services.metrics_service import initialize_metrics_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize application services when the application starts."""
    initialize_metrics_db()
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
