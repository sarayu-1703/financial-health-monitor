"""
schemas/models.py — All Pydantic request/response models.
No raw dicts in route handlers.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class HealthStatus(str, Enum):
    GREEN = "Green"
    AMBER = "Amber"
    RED   = "Red"


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------

class RunRequest(BaseModel):
    prompt: str = Field(
        ...,
        description="Natural-language question from the user.",
        examples=["Give me a financial health report for April 2026"],
    )
    year: int  = Field(2026, ge=2020, le=2100)
    month: int = Field(..., ge=1, le=12)


# ---------------------------------------------------------------------------
# Sub-models used inside the report
# ---------------------------------------------------------------------------

class CategorySpend(BaseModel):
    category: str
    spend:    float
    budget:   Optional[float] = None
    over_by:  Optional[float] = None  # positive means overspent


class BudgetDimension(BaseModel):
    status:            HealthStatus
    overspent_cats:    list[CategorySpend]
    all_category_data: list[CategorySpend]
    summary:           str


class TrendDimension(BaseModel):
    status:           HealthStatus
    current_spend:    float
    previous_spend:   float
    change_pct:       float
    current_income:   float
    net_cash_flow:    float
    summary:          str


class ConcentrationDimension(BaseModel):
    status:              HealthStatus
    top_category:        str
    top_category_pct:    float
    largest_transaction: Optional[dict] = None
    summary:             str


# ---------------------------------------------------------------------------
# Main report
# ---------------------------------------------------------------------------

class HealthReport(BaseModel):
    month:            str           # e.g. "2026-04"
    overall_status:   HealthStatus
    budget:           BudgetDimension
    trend:            TrendDimension
    concentration:    ConcentrationDimension
    executive_summary: list[str]   # 3 bullet points
    remediation:      Optional[list[str]] = None  # only when RED
    agents_involved:  list[str]


class RunResponse(BaseModel):
    session_id:  str
    report:      HealthReport
    raw_prompt:  str


# ---------------------------------------------------------------------------
# Health endpoint
# ---------------------------------------------------------------------------

class HealthResponse(BaseModel):
    service:  str
    version:  str
    status:   str = "ok"


# ---------------------------------------------------------------------------
# History endpoint
# ---------------------------------------------------------------------------

class SessionRecord(BaseModel):
    session_id:  str
    agent_id:    Optional[str] = None
    created_at:  Optional[datetime] = None
    updated_at:  Optional[datetime] = None


class HistoryResponse(BaseModel):
    sessions: list[SessionRecord]
    total:    int
