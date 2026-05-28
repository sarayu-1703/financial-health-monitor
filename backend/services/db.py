"""
services/db.py — Reusable PostgreSQL access layer.

ALL database queries in the project go through this module.
No raw SQL strings scattered elsewhere.
Uses SQLAlchemy core (not ORM) for connection pooling + parameterised queries.
"""

from __future__ import annotations

from contextlib import contextmanager
from decimal import Decimal
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Connection

from backend.config import settings

# ---------------------------------------------------------------------------
# Engine (connection pool) — created once at import time
# ---------------------------------------------------------------------------
_engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,      # test connections before use
    pool_size=5,
    max_overflow=10,
)


@contextmanager
def get_conn() -> Generator[Connection, None, None]:
    """Yield a raw SQLAlchemy connection; auto-commit and close on exit."""
    with _engine.connect() as conn:
        yield conn


# ---------------------------------------------------------------------------
# Query helpers
# ---------------------------------------------------------------------------

def fetch_transactions(year: int, month: int) -> list[dict]:
    """Return all transactions for a given year-month."""
    sql = text("""
        SELECT txn_id, date, description, merchant, amount, category
        FROM   transactions
        WHERE  EXTRACT(YEAR  FROM date) = :year
          AND  EXTRACT(MONTH FROM date) = :month
        ORDER  BY date
    """)
    with get_conn() as conn:
        rows = conn.execute(sql, {"year": year, "month": month}).mappings().all()
    return [dict(r) for r in rows]


def fetch_budgets() -> list[dict]:
    """Return all monthly budget limits."""
    sql = text("SELECT category, monthly_limit FROM budgets ORDER BY category")
    with get_conn() as conn:
        rows = conn.execute(sql).mappings().all()
    return [dict(r) for r in rows]


def fetch_spend_by_category(year: int, month: int) -> list[dict]:
    """
    Return total absolute spend per spending category for the month.
    Excludes Income and Rent (not discretionary).
    """
    sql = text("""
        SELECT   category,
                 ABS(SUM(amount)) AS total_spend
        FROM     transactions
        WHERE    EXTRACT(YEAR  FROM date) = :year
          AND    EXTRACT(MONTH FROM date) = :month
          AND    amount < 0
          AND    category NOT IN ('Income', 'Rent')
        GROUP BY category
        ORDER BY total_spend DESC
    """)
    with get_conn() as conn:
        rows = conn.execute(sql, {"year": year, "month": month}).mappings().all()
    return [{"category": r["category"], "total_spend": float(r["total_spend"])} for r in rows]


def fetch_total_spend(year: int, month: int) -> float:
    """Total absolute discretionary spend for the month (excl. Income, Rent)."""
    sql = text("""
        SELECT COALESCE(ABS(SUM(amount)), 0) AS total
        FROM   transactions
        WHERE  EXTRACT(YEAR  FROM date) = :year
          AND  EXTRACT(MONTH FROM date) = :month
          AND  amount < 0
          AND  category NOT IN ('Income', 'Rent')
    """)
    with get_conn() as conn:
        result = conn.execute(sql, {"year": year, "month": month}).scalar()
    return float(result or 0)


def fetch_total_income(year: int, month: int) -> float:
    """Total income for the month."""
    sql = text("""
        SELECT COALESCE(SUM(amount), 0) AS total
        FROM   transactions
        WHERE  EXTRACT(YEAR  FROM date) = :year
          AND  EXTRACT(MONTH FROM date) = :month
          AND  amount > 0
    """)
    with get_conn() as conn:
        result = conn.execute(sql, {"year": year, "month": month}).scalar()
    return float(result or 0)


def fetch_largest_transaction(year: int, month: int) -> dict | None:
    """Return the single largest spending transaction for the month."""
    sql = text("""
        SELECT txn_id, date, description, merchant, amount, category
        FROM   transactions
        WHERE  EXTRACT(YEAR  FROM date) = :year
          AND  EXTRACT(MONTH FROM date) = :month
          AND  amount < 0
        ORDER  BY amount ASC   -- most negative = biggest spend
        LIMIT  1
    """)
    with get_conn() as conn:
        row = conn.execute(sql, {"year": year, "month": month}).mappings().first()
    if row is None:
        return None
    r = dict(row)
    r["amount"] = float(r["amount"])
    return r


def fetch_past_run_sessions() -> list[dict]:
    """
    Return lightweight session metadata from Agno's storage table.
    Agno (v1.x) stores sessions in a table called `agent_sessions`.
    Falls back gracefully if the table doesn't exist yet.
    """
    sql = text("""
        SELECT session_id, created_at, updated_at, agent_id
        FROM   agent_sessions
        ORDER  BY created_at DESC
        LIMIT  50
    """)
    try:
        with get_conn() as conn:
            rows = conn.execute(sql).mappings().all()
        return [dict(r) for r in rows]
    except Exception:
        return []
