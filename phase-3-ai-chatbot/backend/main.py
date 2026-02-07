"""FastAPI application entry point.

This module configures the FastAPI app with CORS, routers, and lifespan management.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from routes import tasks, auth
from db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Handles startup and shutdown events.
    """
    # Startup
    print("Starting up...")
    await init_db()
    yield
    # Shutdown
    print("Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Todo API",
    description="Task management API with JWT authentication",
    version="2.0.0",
    lifespan=lifespan
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(
    tasks.router,
    prefix="/api/{user_id}/tasks",
    tags=["tasks"]
)

app.include_router(
    auth.router,
    prefix="/api/auth",
    tags=["auth"]
)


@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {"status": "healthy", "message": "Todo API is running"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
