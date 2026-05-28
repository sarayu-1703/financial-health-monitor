"""
agents/concentration_agent.py — Spend concentration specialist.

Identifies where money is going; flags if one category dominates (> 40% of spend)
or if there is an unusually large single transaction.
"""

from __future__ import annotations

from agno.agent import Agent
from agno.models.anthropic import Claude

from backend.config import settings
from backend.tools.finance_tools import get_largest_transaction, spend_by_category


def build_concentration_agent() -> Agent:
    """
    Factory that returns a configured Concentration Agent.
    The agent analyses spend distribution and flags concentration risk.
    """
    return Agent(
        name="Concentration Agent",
        role="Spend Concentration Analyst",
        model=Claude(id=settings.agno_model),
        tools=[spend_by_category, get_largest_transaction],
        instructions=[
            "You are a spend concentration analyst. Your ONLY job is concentration analysis.",
            "1. Call spend_by_category(year, month) to get spend per category.",
            "2. Compute total_spend = sum of all category spends.",
            "3. For the top category, compute top_pct = (top_category_spend / total_spend) * 100.",
            "4. Call get_largest_transaction(year, month) to find any single large charge.",
            "5. Assign concentration status:",
            "   - RED    if top_pct > 40% OR largest single transaction > 10000 INR",
            "   - AMBER  if top_pct is between 30–40%",
            "   - GREEN  if top_pct <= 30%",
            "6. Return your analysis in this exact JSON format:",
            "   {",
            '     "status": "Green|Amber|Red",',
            '     "top_category": "<category name>",',
            '     "top_category_pct": <number, 2 decimal places>,',
            '     "largest_transaction": {txn_id, date, description, merchant, amount, category} or null,',
            '     "summary": "one sentence summarising concentration findings"',
            "   }",
            "NEVER invent numbers. All figures come exclusively from the tool results.",
            "Return ONLY the JSON object. No preamble, no markdown fences.",
        ],
        show_tool_calls=True,
        markdown=False,
    )
