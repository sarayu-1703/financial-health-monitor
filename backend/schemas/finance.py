from pydantic import BaseModel
from typing import List


class BudgetItem(BaseModel):
    category: str
    spent: float
    limit: float
    status: str


class TrendItem(BaseModel):
    month: str
    total_spent: float


class ConcentrationItem(BaseModel):
    category: str
    percentage: float


class FinancialResponse(BaseModel):
    overall_status: str
    budget_analysis: List[BudgetItem]
    trend_analysis: List[TrendItem]
    concentration_analysis: List[ConcentrationItem]
    ai_insights: str
    agents_used: List[str]
