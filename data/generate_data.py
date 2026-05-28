"""
Fyntwin synthetic transaction generator (standard library only).
Produces transactions.csv + seed.sql for Jan–Apr 2026.

Guarantees:
  Feb 2026 -> GREEN  (under budget, spend < Jan)
  Apr 2026 -> RED    (over budget in Food/Entertainment/Shopping, big spike, concentration)
"""

import csv
import random
import uuid
from datetime import date, timedelta
from decimal import Decimal

random.seed(42)

CATEGORIES = ["Food", "Transport", "Utilities", "Entertainment", "Shopping", "Other", "Rent"]
INCOME_CAT = "Income"

BUDGETS = {
    "Food": 8000,
    "Transport": 3000,
    "Utilities": 2500,
    "Entertainment": 3000,
    "Shopping": 5000,
    "Other": 2000,
}

MERCHANTS = {
    "Food": ["Swiggy", "Zomato", "Big Bazaar", "D-Mart", "Fresh Basket", "Cafe Coffee Day", "Haldirams"],
    "Transport": ["Ola", "Uber", "IRCTC", "IndiGo", "Indian Oil", "HP Petrol"],
    "Utilities": ["APSEB", "Airtel", "Jio", "Hathway Broadband", "BSNL"],
    "Entertainment": ["BookMyShow", "Netflix", "Spotify", "Amazon Prime", "PVR Cinemas", "Inox"],
    "Shopping": ["Amazon", "Flipkart", "Myntra", "Meesho", "Ajio", "Nykaa"],
    "Other": ["ATM Withdrawal", "Bank Charges", "Medical Pharmacy", "Practo", "Apollo"],
    "Rent": ["House Rent"],
    "Income": ["Salary Credit", "Freelance Payment", "Bonus Credit"],
}

MONTH_TARGETS = {
    # (month, year): {cat: target_spend}
    (1, 2026): {"Food": 7200, "Transport": 2600, "Utilities": 2300, "Entertainment": 2500, "Shopping": 4200, "Other": 1500, "Rent": 12000},
    (2, 2026): {"Food": 5800, "Transport": 1900, "Utilities": 2100, "Entertainment": 1800, "Shopping": 2800, "Other": 900,  "Rent": 12000},  # GREEN
    (3, 2026): {"Food": 6900, "Transport": 2400, "Utilities": 2200, "Entertainment": 2700, "Shopping": 3800, "Other": 1300, "Rent": 12000},
    (4, 2026): {"Food": 11500, "Transport": 3200, "Utilities": 2400, "Entertainment": 6200, "Shopping": 18000, "Other": 1800, "Rent": 12000},  # RED
}

INCOME_AMOUNTS = {
    (1, 2026): 65000,
    (2, 2026): 65000,
    (3, 2026): 65000,
    (4, 2026): 65000,
}


def random_date(year, month):
    if month == 12:
        end = date(year + 1, 1, 1)
    else:
        end = date(year, month + 1, 1)
    start = date(year, month, 1)
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta - 1))


def gen_transactions():
    rows = []

    for (month, year), targets in MONTH_TARGETS.items():
        # Income credit (usually on 1st or 2nd)
        income_date = date(year, month, random.randint(1, 2))
        income_amount = INCOME_AMOUNTS[(month, year)]
        rows.append({
            "txn_id": str(uuid.uuid4()),
            "date": income_date.isoformat(),
            "description": "Monthly Salary",
            "merchant": random.choice(MERCHANTS["Income"]),
            "amount": str(income_amount),
            "category": "Income",
        })

        # Spending transactions per category
        for cat, target in targets.items():
            if cat == "Rent":
                # Single rent payment
                rows.append({
                    "txn_id": str(uuid.uuid4()),
                    "date": date(year, month, random.randint(1, 5)).isoformat(),
                    "description": "Monthly House Rent",
                    "merchant": "House Rent",
                    "amount": str(-target),
                    "category": "Rent",
                })
                continue

            # Apr Shopping: add one large single transaction (concentration trigger)
            if month == 4 and cat == "Shopping":
                # Big purchase ~12000
                big_amount = 12000
                rows.append({
                    "txn_id": str(uuid.uuid4()),
                    "date": random_date(year, month).isoformat(),
                    "description": "iPhone Purchase EMI",
                    "merchant": "Apple India",
                    "amount": str(-big_amount),
                    "category": "Shopping",
                })
                remaining = target - big_amount
                n_txns = random.randint(4, 7)
                amounts = _split(remaining, n_txns)
                for amt in amounts:
                    rows.append({
                        "txn_id": str(uuid.uuid4()),
                        "date": random_date(year, month).isoformat(),
                        "description": f"{cat} purchase",
                        "merchant": random.choice(MERCHANTS[cat]),
                        "amount": str(-amt),
                        "category": cat,
                    })
                continue

            n_txns = random.randint(3, 9)
            amounts = _split(target, n_txns)
            for amt in amounts:
                rows.append({
                    "txn_id": str(uuid.uuid4()),
                    "date": random_date(year, month).isoformat(),
                    "description": f"{cat} expense",
                    "merchant": random.choice(MERCHANTS[cat]),
                    "amount": str(-amt),
                    "category": cat,
                })

    return rows


def _split(total, n):
    """Split total into n positive integer parts."""
    if n <= 1:
        return [total]
    cuts = sorted(random.sample(range(1, total), min(n - 1, total - 1)))
    parts = []
    prev = 0
    for c in cuts:
        parts.append(c - prev)
        prev = c
    parts.append(total - prev)
    return [max(1, p) for p in parts]


def write_csv(rows, path="transactions.csv"):
    fields = ["txn_id", "date", "description", "merchant", "amount", "category"]
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {len(rows)} rows to {path}")


def write_sql(rows, path="seed.sql"):
    schema = """-- ============================================================
--  Fyntwin schema + seed  (auto-generated by generate_data.py)
-- ============================================================

CREATE TABLE IF NOT EXISTS categories (
    name TEXT PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS budgets (
    category      TEXT PRIMARY KEY REFERENCES categories(name),
    monthly_limit NUMERIC(12,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS transactions (
    txn_id      TEXT PRIMARY KEY,
    date        DATE NOT NULL,
    description TEXT,
    merchant    TEXT,
    amount      NUMERIC(12,2) NOT NULL,   -- negative = spend, positive = income
    category    TEXT REFERENCES categories(name)
);

CREATE INDEX IF NOT EXISTS idx_txn_date     ON transactions(date);
CREATE INDEX IF NOT EXISTS idx_txn_category ON transactions(category);

-- Categories
INSERT INTO categories (name) VALUES
    ('Food'),('Transport'),('Utilities'),('Entertainment'),
    ('Shopping'),('Other'),('Income'),('Rent')
ON CONFLICT DO NOTHING;

-- Monthly budget limits (INR)
INSERT INTO budgets (category, monthly_limit) VALUES
    ('Food',          8000),
    ('Transport',     3000),
    ('Utilities',     2500),
    ('Entertainment', 3000),
    ('Shopping',      5000),
    ('Other',         2000)
ON CONFLICT (category) DO UPDATE SET monthly_limit = EXCLUDED.monthly_limit;

-- Transactions\n"""

    lines = [schema]
    for r in rows:
        desc = r["description"].replace("'", "''")
        merch = r["merchant"].replace("'", "''")
        lines.append(
            f"INSERT INTO transactions (txn_id, date, description, merchant, amount, category) VALUES "
            f"('{r['txn_id']}', '{r['date']}', '{desc}', '{merch}', {r['amount']}, '{r['category']}') "
            f"ON CONFLICT DO NOTHING;\n"
        )

    with open(path, "w") as f:
        f.writelines(lines)
    print(f"Wrote SQL to {path}")


def print_summary(rows):
    from collections import defaultdict

    by_month = defaultdict(lambda: defaultdict(float))
    for r in rows:
        ym = r["date"][:7]
        amt = float(r["amount"])
        by_month[ym][r["category"]] += amt

    budgets_ref = BUDGETS

    print("\n=== Sanity Summary ===")
    for ym in sorted(by_month):
        cats = by_month[ym]
        disc_spend = sum(-v for k, v in cats.items() if k not in ("Income", "Rent") and v < 0)
        income = cats.get("Income", 0)
        over = [k for k, v in cats.items() if k in budgets_ref and -v > budgets_ref[k]]

        # Simple status
        prev_months = [m for m in sorted(by_month) if m < ym]
        trend = ""
        if prev_months:
            prev_disc = sum(-v for k, v in by_month[prev_months[-1]].items() if k not in ("Income", "Rent") and v < 0)
            if disc_spend > prev_disc * 1.1:
                trend = "RISING"
            else:
                trend = "ok"

        # Top cat
        spend_cats = {k: -v for k, v in cats.items() if k not in ("Income", "Rent") and v < 0}
        total_spend = sum(spend_cats.values()) or 1
        top = max(spend_cats, key=spend_cats.get, default="")
        top_pct = round(spend_cats.get(top, 0) / total_spend * 100)

        n_risk = (1 if over else 0) + (1 if trend == "RISING" else 0) + (1 if top_pct > 40 else 0)
        status = "GREEN" if n_risk == 0 else ("RED" if n_risk >= 2 else "AMBER")

        conc = f"concentration({top} {top_pct}%)" if top_pct > 40 else ""
        over_str = f"over={over}" if over else ""
        details = "; ".join(x for x in [over_str, conc] if x)
        print(f"{ym}  disc_spend={int(disc_spend):6d}  trend={trend or 'N/A':6s}  -> {status:5s}  {details}")


if __name__ == "__main__":
    rows = gen_transactions()
    write_csv(rows)
    write_sql(rows)
    print_summary(rows)
