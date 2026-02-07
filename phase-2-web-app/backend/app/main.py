"""
FastAPI application entry point.

This is the main application file that initializes FastAPI,
configures middleware, and registers routers.

Spec Reference: @specs/architecture.md
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import init_db
from app.routers import auth, tasks


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.

    Startup:
        - Initialize database tables

    Shutdown:
        - Cleanup resources (handled automatically)
    """
    # Startup
    print("Starting FastAPI application...")
    await init_db()
    print("Database initialized successfully")

    yield

    # Shutdown
    print("Shutting down FastAPI application...")


# Create FastAPI app
app = FastAPI(
    title="Todo Manager API",
    description="RESTful API for todo management with authentication",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# Configure CORS
cors_origins_list = [origin.strip() for origin in settings.cors_origins.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register routers
app.include_router(auth.router)
app.include_router(tasks.router)


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint - API health check.

    Returns:
        Welcome message and API version
    """
    return {
        "message": "Welcome to Todo Manager API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "operational",
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.

    Returns:
        Health status
    """
    return {"status": "healthy", "service": "todo-api"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info",
    )
