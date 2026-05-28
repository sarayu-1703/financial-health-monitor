from agno.agent import Agent

from backend.tools.finance_tools import (
    compare_months
)

def analyze_trend(current_month: str, previous_month: str):
    data = compare_months(
        current_month,
        previous_month
    )

    return data


trend_agent = Agent(
    name="Trend Agent",
    description="Analyzes spending trends"
)