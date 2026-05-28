"""
routes/agent.py — POST /api/v1/run

Accepts a natural-language prompt + year/month, runs the Agno workflow,
and returns a structured HealthReport.
"""

import uuid

from fastapi import APIRouter, HTTPException

from backend.agents.team    import run_financial_workflow
from backend.schemas.models import RunRequest, RunResponse

router = APIRouter()


@router.post("/run", response_model=RunResponse)
def run_analysis(body: RunRequest) -> RunResponse:
    """
    Accept a natural-language financial query.
    Orchestrate the parallel agent team + conditional workflow.
    Return the structured health report.
    """
    try:
        report = run_financial_workflow(
            year=body.year,
            month=body.month,
            user_prompt=body.prompt,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return RunResponse(
        session_id=str(uuid.uuid4()),
        report=report,
        raw_prompt=body.prompt,
    )
