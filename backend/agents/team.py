from backend.agents.budget_agent import (
    analyze_budget
)

from backend.agents.trend_agent import (
    analyze_trend
)

from backend.agents.concentration_agent import (
    concentration_analysis
)

from backend.agents.insight_agent import (
    generate_insights
)

from backend.services.history_store import (
    save_history
)


def convert_decimals(obj):
    if isinstance(obj, list):
        return [convert_decimals(i) for i in obj]

    if isinstance(obj, dict):
        return {
            k: convert_decimals(v)
            for k, v in obj.items()
        }

    try:
        return float(obj)
    except:
        return obj


def run_financial_analysis(
    current_month: str,
    previous_month: str
):
    budget_result = analyze_budget(current_month)

    trend_result = analyze_trend(
        current_month,
        previous_month
    )

    concentration_result = concentration_analysis(
        current_month
    )

    risk_count = 0

    over_budget = [
        item
        for item in budget_result
        if item["status"] == "OVER BUDGET"
    ]

    if len(over_budget) >= 2:
        risk_count += 1

    if trend_result and len(trend_result) > 0:
        risk_count += 1

    high_concentration = any(
        float(item["percentage"]) > 40
        for item in concentration_result
    )

    if high_concentration:
        risk_count += 1

    if risk_count >= 2:
        overall_status = "RED"
    elif risk_count == 1:
        overall_status = "AMBER"
    else:
        overall_status = "GREEN"

    result = {
        "overall_status": overall_status,
        "budget_analysis": budget_result,
        "trend_analysis": trend_result,
        "concentration_analysis": concentration_result
    }

    clean_result = convert_decimals(result)

    if overall_status == "RED":
        insights = generate_insights(
            clean_result
        )
    else:
        insights = (
            "Financial condition is stable. "
            "Continue maintaining your budgets carefully."
        )

    clean_result["ai_insights"] = insights

    clean_result["agents_used"] = [
        "Budget Agent",
        "Trend Agent",
        "Concentration Agent",
        "Insight Agent"
    ]

    save_history(clean_result)

    return clean_result