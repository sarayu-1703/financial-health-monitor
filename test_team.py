from backend.agents.team import (
    run_financial_analysis
)

result = run_financial_analysis(
    "2026-04",
    "2026-03"
)

print(result)