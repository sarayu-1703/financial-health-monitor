from agno.agent import Agent

from backend.tools.finance_tools import (
    spend_by_category
)


def concentration_analysis(month: str):
    data = spend_by_category(month)

    total = sum(
        float(item["total_spent"])
        for item in data
    )

    result = []

    for item in data:
        percent = (
            float(item["total_spent"]) / total
        ) * 100

        result.append({
            "category": item["category"],
            "percentage": round(percent, 2)
        })

    return result


concentration_agent = Agent(
    name="Concentration Agent",
    description="Analyzes spending concentration"
)
