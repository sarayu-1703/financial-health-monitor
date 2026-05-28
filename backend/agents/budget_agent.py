from agno.agent import Agent

from backend.tools.finance_tools import (
    spend_by_category,
    get_budgets
)

def analyze_budget(month: str):
    spending = spend_by_category(month)
    budgets = get_budgets()

    budget_map = {
        b["category"]: float(b["monthly_limit"])
        for b in budgets
    }

    analysis = []

    for item in spending:
        category = item["category"]
        spent = float(item["total_spent"])

        limit = budget_map.get(category, 0)

        if spent > limit:
            status = "OVER BUDGET"
        elif spent > limit * 0.8:
            status = "NEAR LIMIT"
        else:
            status = "SAFE"

        analysis.append({
            "category": category,
            "spent": spent,
            "limit": limit,
            "status": status
        })

    return analysis


budget_agent = Agent(
    name="Budget Agent",
    description="Analyzes monthly category spending"
)
