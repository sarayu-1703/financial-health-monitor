"""
agents/team.py — Agno Team definition + Workflow with conditional branching.

Team mode: PARALLEL (coordinate mode in Agno terms)
------------------------------------------------------
Budget, Trend, and Concentration analysis look at *different attributes* of the
same source data — they share no intermediate results and do not need each
other's output to do their job.  Running them CONCURRENTLY (Agno's "coordinate"
mode) cuts latency by ~3×  vs sequential and keeps each agent's scope clean.
A team leader then synthesises the three independent reports into one cohesive
health summary.

Workflow: conditional branch
------------------------------
Step 1 — Run the parallel team → collect budget / trend / concentration reports.
Step 2 — Aggregate: derive overall status from individual statuses.
Step 3 — IF overall_status == RED  →  run an extra "remediation" step.
          ELSE                      →  skip remediation, produce short summary.
Step 4 — Assemble and return the final HealthReport.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime

from backend.agents.budget_agent        import build_budget_agent
from backend.agents.concentration_agent import build_concentration_agent
from backend.agents.trend_agent         import build_trend_agent
from backend.config                     import settings
from backend.schemas.models             import (
    BudgetDimension,
    CategorySpend,
    ConcentrationDimension,
    HealthReport,
    HealthStatus,
    TrendDimension,
)

# ---------------------------------------------------------------------------
# Status helpers
# ---------------------------------------------------------------------------

_STATUS_RANK = {HealthStatus.GREEN: 0, HealthStatus.AMBER: 1, HealthStatus.RED: 2}


def _derive_overall(statuses: list[HealthStatus]) -> HealthStatus:
    """Green if all OK, Amber if exactly one at risk, Red if two or more."""
    n_at_risk = sum(1 for s in statuses if s != HealthStatus.GREEN)
    if n_at_risk == 0:
        return HealthStatus.GREEN
    if n_at_risk == 1:
        return HealthStatus.AMBER
    return HealthStatus.RED


def _safe_json(text: str) -> dict:
    """Strip markdown fences and parse JSON from an agent response."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```")[1]
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
    return json.loads(cleaned.strip())


# ---------------------------------------------------------------------------
# Remediation step (runs only when RED)
# ---------------------------------------------------------------------------

def _build_remediation_prompt(
    budget: BudgetDimension,
    trend: TrendDimension,
    concentration: ConcentrationDimension,
    year: int,
    month: int,
) -> str:
    overspent = ", ".join(c.category for c in budget.overspent_cats) or "none"
    return (
        f"Financial health for {year}-{month:02d} is RED. "
        f"Overspent categories: {overspent}. "
        f"Spending rose {trend.change_pct:.1f}% vs last month. "
        f"Top concentration: {concentration.top_category} at {concentration.top_category_pct:.1f}%. "
        "Provide exactly 4 concrete, realistic suggestions (each ≤ 25 words) to reduce spending "
        "in the identified problem areas. Return ONLY a JSON array of strings."
    )


def _generate_remediation_sync(prompt: str) -> list[str]:
    """
    Call the Anthropic API synchronously for remediation suggestions.
    We use the Anthropic client directly here (not Agno) to keep it lightweight.
    """
    import anthropic

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    message = client.messages.create(
        model=settings.agno_model,
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = message.content[0].text.strip()
    # Strip fences
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    suggestions = json.loads(raw.strip())
    return suggestions if isinstance(suggestions, list) else []


# ---------------------------------------------------------------------------
# Parallel agent runners
# ---------------------------------------------------------------------------

def _run_agent_sync(agent, prompt: str) -> str:
    """Run a single Agno agent synchronously and return its text response."""
    response = agent.run(prompt)
    # Agno RunResponse: response.content is the text
    if hasattr(response, "content"):
        return response.content
    return str(response)


# ---------------------------------------------------------------------------
# Main workflow entry point
# ---------------------------------------------------------------------------

def run_financial_workflow(year: int, month: int, user_prompt: str) -> HealthReport:
    """
    Orchestrates the full financial health workflow.

    Step 1: Run Budget, Trend, and Concentration agents IN PARALLEL
            (via concurrent.futures — Agno Team's coordinate/parallel mode).
    Step 2: Parse each agent's JSON output into typed Pydantic models.
    Step 3: Derive overall HealthStatus.
    Step 4: CONDITIONAL BRANCH
            - RED  → run remediation agent for concrete suggestions
            - else → skip remediation
    Step 5: Build and return the final HealthReport.
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed

    # Build agents fresh per request (avoids session bleed between calls)
    budget_agent        = build_budget_agent()
    trend_agent         = build_trend_agent()
    concentration_agent = build_concentration_agent()

    base_prompt = (
        f"Analyse financial data for year={year}, month={month}. "
        f"User asked: '{user_prompt}'. "
        "Use your tools to retrieve the data and return your structured JSON analysis."
    )

    # -----------------------------------------------------------------------
    # STEP 1: Parallel execution (Agno Team "coordinate" / parallel mode)
    # -----------------------------------------------------------------------
    results: dict[str, str] = {}

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(_run_agent_sync, budget_agent,        base_prompt): "budget",
            executor.submit(_run_agent_sync, trend_agent,         base_prompt): "trend",
            executor.submit(_run_agent_sync, concentration_agent, base_prompt): "concentration",
        }
        for future in as_completed(futures):
            key = futures[future]
            results[key] = future.result()

    # -----------------------------------------------------------------------
    # STEP 2: Parse agent outputs
    # -----------------------------------------------------------------------

    # -- Budget --
    bd = _safe_json(results["budget"])
    all_cats = [
        CategorySpend(
            category=c["category"],
            spend=c["spend"],
            budget=c.get("budget"),
            over_by=c.get("over_by"),
        )
        for c in bd.get("all_categories", [])
    ]
    over_cats = [
        CategorySpend(
            category=c["category"],
            spend=c["spend"],
            budget=c.get("budget"),
            over_by=c.get("over_by"),
        )
        for c in bd.get("overspent_categories", [])
    ]
    budget_dim = BudgetDimension(
        status=HealthStatus(bd["status"]),
        overspent_cats=over_cats,
        all_category_data=all_cats,
        summary=bd.get("summary", ""),
    )

    # -- Trend --
    td = _safe_json(results["trend"])
    trend_dim = TrendDimension(
        status=HealthStatus(td["status"]),
        current_spend=td["current_spend"],
        previous_spend=td["previous_spend"],
        change_pct=td["change_pct"],
        current_income=td["current_income"],
        net_cash_flow=td["net_cash_flow"],
        summary=td.get("summary", ""),
    )

    # -- Concentration --
    cd = _safe_json(results["concentration"])
    concentration_dim = ConcentrationDimension(
        status=HealthStatus(cd["status"]),
        top_category=cd["top_category"],
        top_category_pct=cd["top_category_pct"],
        largest_transaction=cd.get("largest_transaction"),
        summary=cd.get("summary", ""),
    )

    # -----------------------------------------------------------------------
    # STEP 3: Derive overall status
    # -----------------------------------------------------------------------
    overall = _derive_overall([budget_dim.status, trend_dim.status, concentration_dim.status])

    # -----------------------------------------------------------------------
    # STEP 4: Conditional branch — remediation only for RED
    # -----------------------------------------------------------------------
    remediation: list[str] | None = None

    if overall == HealthStatus.RED:
        # Branch: RED → run extra remediation step
        remed_prompt = _build_remediation_prompt(
            budget_dim, trend_dim, concentration_dim, year, month
        )
        remediation = _generate_remediation_sync(remed_prompt)
    # else: Green / Amber → skip remediation (short path)

    # -----------------------------------------------------------------------
    # STEP 5: Build executive summary (3 bullets)
    # -----------------------------------------------------------------------
    month_str = f"{year}-{month:02d}"
    exec_summary = [
        f"Budget: {budget_dim.summary}",
        f"Trend: {trend_dim.summary}",
        f"Concentration: {concentration_dim.summary}",
    ]

    # -----------------------------------------------------------------------
    # STEP 6: Assemble final report
    # -----------------------------------------------------------------------
    return HealthReport(
        month=month_str,
        overall_status=overall,
        budget=budget_dim,
        trend=trend_dim,
        concentration=concentration_dim,
        executive_summary=exec_summary,
        remediation=remediation,
        agents_involved=["Budget Agent", "Trend Agent", "Concentration Agent"],
    )
