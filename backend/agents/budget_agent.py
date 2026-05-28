"""
agents/budget_agent.py — Budget health specialist.

Compares actual spend per category against monthly budget limits.
Flags overspent categories and computes overall budget health status.
"""

from __future__ import annotations

from agno.agent import Agent
from agno.models.anthropic import Claude

from backend.config import settings
from backend.tools.finance_tools import get_budgets, spend_by_category


def build_budget_agent() -> Agent:
    """
    Factory that returns a configured Budget Agent.
    The agent analyses spend-vs-budget for every spending category
    and returns a structured budget health assessment.
    """
    return Agent(
        name="Budget Agent",
        role="Budget Health Specialist",
        model=Claude(id=settings.agno_model),
        tools=[spend_by_category, get_budgets],
        instructions=[
            "You are a budget health analyst. Your ONLY job is budget analysis.",
            "1. Call spend_by_category(year, month) to get actual spend per category.",
            "2. Call get_budgets() to get the monthly limit for each category.",
            "3. For each spending category, compute: over_by = actual_spend - monthly_limit.",
            "   If over_by > 0, the category is overspent.",
            "4. Assign budget status:",
            "   - GREEN  if no category is overspent",
            "   - AMBER  if 1 category is overspent",
            "   - RED    if 2 or more categories are overspent",
            "5. Return your analysis in this exact JSON format:",
            "   {",
            '     "status": "Green|Amber|Red",',
            '     "overspent_categories": [{"category":"...", "spend":..., "budget":..., "over_by":...}],',
            '     "all_categories": [{"category":"...", "spend":..., "budget":..., "over_by":...}],',
            '     "summary": "one sentence summarising budget health"',
            "   }",
            "NEVER invent numbers. All figures come exclusively from the tool results.",
            "Return ONLY the JSON object. No preamble, no markdown fences.",
        ],
        show_tool_calls=True,
        markdown=False,
    )
