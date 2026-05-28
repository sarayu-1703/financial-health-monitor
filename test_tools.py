from backend.tools.finance_tools import (
    get_transactions,
    get_budgets,
    spend_by_category
)

print(get_budgets())

print(spend_by_category("2026-04"))