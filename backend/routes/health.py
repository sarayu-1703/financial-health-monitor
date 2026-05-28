"""
routes/health.py — GET /api/v1/health  and  GET /api/v1/history
"""

from fastapi import APIRouter

from backend.config         import settings
from backend.schemas.models import HealthResponse, HistoryResponse, SessionRecord
from backend.services       import db

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Service liveness probe — returns name, version, and status."""
    return HealthResponse(
        service=settings.app_name,
        version=settings.app_version,
        status="ok",
    )


@router.get("/history", response_model=HistoryResponse)
def get_history() -> HistoryResponse:
    """
    Return past agent session runs stored by Agno in Postgres.
    Falls back to an empty list if the sessions table doesn't exist yet.
    """
    raw = db.fetch_past_run_sessions()
    sessions = [
        SessionRecord(
            session_id=str(r.get("session_id", "")),
            agent_id=r.get("agent_id"),
            created_at=r.get("created_at"),
            updated_at=r.get("updated_at"),
        )
        for r in raw
    ]
    return HistoryResponse(sessions=sessions, total=len(sessions))
