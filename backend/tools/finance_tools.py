from sqlalchemy import text
from backend.services.db import engine


def get_transactions(month: str):
    query = text("""
        SELECT *
        FROM transactions
        WHERE TO_CHAR(date, 'YYYY-MM') = :month
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {"month": month})

    return [dict(row._mapping) for row in result]


def get_budgets():
    query = text("""
        SELECT *
        FROM budgets
    """)

    with engine.connect() as conn:
        result = conn.execute(query)

    return [dict(row._mapping) for row in result]


def spend_by_category(month: str):
    query = text("""
        SELECT
            category,
            ABS(SUM(amount)) AS total_spent
        FROM transactions
        WHERE amount < 0
          AND TO_CHAR(date, 'YYYY-MM') = :month
        GROUP BY category
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {"month": month})

    return [dict(row._mapping) for row in result]


def compare_months(current_month: str, previous_month: str):
    query = text("""
        SELECT
            TO_CHAR(date, 'YYYY-MM') AS month,
            ABS(SUM(amount)) AS total_spent
        FROM transactions
        WHERE amount < 0
          AND TO_CHAR(date, 'YYYY-MM') IN (:current_month, :previous_month)
        GROUP BY month
    """)

    with engine.connect() as conn:
        result = conn.execute(
            query,
            {
                "current_month": current_month,
                "previous_month": previous_month
            }
        )

    return [dict(row._mapping) for row in result]
