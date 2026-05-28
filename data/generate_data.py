import random
import uuid
from datetime import datetime, timedelta

categories = [
    "Food",
    "Transport",
    "Utilities",
    "Entertainment",
    "Shopping",
    "Other",
    "Income",
    "Rent"
]

merchants = {
    "Food": ["Swiggy", "Zomato", "Cafe"],
    "Transport": ["Uber", "Metro", "Rapido"],
    "Utilities": ["Electricity", "Internet"],
    "Entertainment": ["Netflix", "Movie"],
    "Shopping": ["Amazon", "Flipkart"],
    "Other": ["Misc"],
    "Income": ["Salary"],
    "Rent": ["House Rent"]
}

months = [
    ("2026-01-01", "2026-01-31"),
    ("2026-02-01", "2026-02-28"),
    ("2026-03-01", "2026-03-31"),
    ("2026-04-01", "2026-04-30")
]

transactions = []

for start, end in months:
    start_date = datetime.strptime(start, "%Y-%m-%d")
    end_date = datetime.strptime(end, "%Y-%m-%d")

    for _ in range(random.randint(40, 80)):
        category = random.choice(categories)

        merchant = random.choice(merchants[category])

        if category == "Income":
            amount = random.randint(40000, 70000)
        elif category == "Rent":
            amount = -random.randint(10000, 20000)
        else:
            amount = -random.randint(200, 8000)

        random_days = random.randint(
            0,
            (end_date - start_date).days
        )

        txn_date = start_date + timedelta(days=random_days)

        transactions.append(
            (
                str(uuid.uuid4()),
                txn_date.date(),
                merchant,
                merchant,
                amount,
                category
            )
        )

sql_lines = []

for txn in transactions:
    sql_lines.append(
        f"""
INSERT INTO transactions
(txn_id, date, description, merchant, amount, category)
VALUES
('{txn[0]}', '{txn[1]}', '{txn[2]}', '{txn[3]}', {txn[4]}, '{txn[5]}');
"""
    )

with open("data/transactions.sql", "w") as f:
    f.writelines(sql_lines)

<<<<<<< HEAD
print("Generated transactions.sql successfully!")
=======
print("Generated transactions.sql successfully!")
>>>>>>> 2c4f512 (Final Financial Health Monitor)
