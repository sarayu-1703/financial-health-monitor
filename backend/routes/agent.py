from fastapi import APIRouter

from backend.agents.team import (
    run_financial_analysis
)

from backend.schemas.finance import (
    FinancialResponse
)

router = APIRouter()


@router.post(
    "/run",
    response_model=FinancialResponse
)
def run_agent():
    result = run_financial_analysis(
        "2026-04",
        "2026-03"
    )

    return result
