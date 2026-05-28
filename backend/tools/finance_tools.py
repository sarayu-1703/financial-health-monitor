"""
tools/finance_tools.py — Agno tool functions.

Each function does exactly ONE thing and is backed by the DB access layer.
Tools live here, not in routes or agents.
"""

from __future__ import annotations

from backend.services import db


def get_transactions(year: int, month: int) -> list[dict]:
    """
    Fetch all transactions for the given year and month from the database.
    Returns a list of dicts with keys: txn_id, date, description, merchant, amount, category.
    """
    return db.fetch_transactions(year, month)


def get_budgets() -> list[dict]:
    """
    Fetch all monthly budget limits from the database.
    Returns a list of dicts with keys: category, monthly_limit.
    """
    return db.fetch_budgets()


def spend_by_category(year: int, month: int) -> list[dict]:
    """
    Compute total absolute discretionary spend per category for the given month.
    Excludes Income and Rent. Returns [{category, total_spend}, ...] sorted descending.
    """
    return db.fetch_spend_by_category(year, month)


def get_monthly_totals(year: int, month: int) -> dict:
    """
    Return total discretionary spend, total income, and net cash flow for the month.
    net_cash_flow = income - (discretionary_spend + rent)
    """
    spend  = db.fetch_total_spend(year, month)
    income = db.fetch_total_income(year, month)
    return {
        "total_spend":    spend,
        "total_income":   income,
        "net_cash_flow":  income - spend,
    }


def get_largest_transaction(year: int, month: int) -> dict | None:
    """
    Return the single largest spending transaction (by absolute amount) for the month.
    Returns None if no transactions exist.
    """
    return db.fetch_largest_transaction(year, month)
