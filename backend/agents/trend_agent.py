"""
agents/trend_agent.py — Spending trend specialist.

Compares current month total spend and net cash flow against the previous month.
Flags if spending is rising materially (>10% increase).
"""

from __future__ import annotations

from agno.agent import Agent
from agno.models.anthropic import Claude

from backend.config import settings
from backend.tools.finance_tools import get_monthly_totals


def build_trend_agent() -> Agent:
    """
    Factory that returns a configured Trend Agent.
    The agent performs month-over-month spend and cash-flow analysis.
    """
    return Agent(
        name="Trend Agent",
        role="Spending Trend Analyst",
        model=Claude(id=settings.agno_model),
        tools=[get_monthly_totals],
        instructions=[
            "You are a spending trend analyst. Your ONLY job is trend analysis.",
            "You will receive the target year and month in the user prompt.",
            "1. Call get_monthly_totals(year, month) for the target month.",
            "2. Compute the PREVIOUS month: if month=1, previous=(year-1, 12); else previous=(year, month-1).",
            "3. Call get_monthly_totals(year, prev_month) for the previous month.",
            "4. Compute change_pct = ((current_spend - prev_spend) / prev_spend) * 100.",
            "   If prev_spend is 0, set change_pct = 0.",
            "5. Assign trend status:",
            "   - GREEN  if spending DECREASED vs previous month (change_pct <= 0)",
            "   - AMBER  if spending rose but less than 10% (0 < change_pct < 10)",
            "   - RED    if spending rose 10% or more (change_pct >= 10)",
            "6. Return your analysis in this exact JSON format:",
            "   {",
            '     "status": "Green|Amber|Red",',
            '     "current_spend": <number>,',
            '     "previous_spend": <number>,',
            '     "change_pct": <number, 2 decimal places>,',
            '     "current_income": <number>,',
            '     "net_cash_flow": <number>,',
            '     "summary": "one sentence summarising the trend"',
            "   }",
            "NEVER invent numbers. All figures come exclusively from the tool results.",
            "Return ONLY the JSON object. No preamble, no markdown fences.",
        ],
        show_tool_calls=True,
        markdown=False,
    )
