from fastapi import APIRouter

from backend.services.history_store import (
    get_history
)

router = APIRouter()


@router.get("/health")
def health():
    return {
        "service": "Financial Health Monitor",
        "version": "1.0.0",
        "status": "running"
    }


@router.get("/history")
def history():
    return get_history()