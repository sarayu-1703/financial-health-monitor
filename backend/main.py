"""
main.py — FastAPI application entry point.

Run with:
    uvicorn backend.main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config          import settings
from backend.routes.agent    import router as agent_router
from backend.routes.health   import router as health_router

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Intelligent personal-finance assistant that analyses budget health, "
        "spending trends, and concentration risk using an Agno multi-agent team."
    ),
)

# Allow the frontend (any origin in dev; restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes under /api/v1/
app.include_router(health_router, prefix="/api/v1")
app.include_router(agent_router,  prefix="/api/v1")


@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.app_name} v{settings.app_version}",
        "docs": "/docs",
    }
