CREATE TABLE IF NOT EXISTS categories (
    name TEXT PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS budgets (
    category TEXT PRIMARY KEY REFERENCES categories(name),
    monthly_limit NUMERIC(12,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS transactions (
    txn_id TEXT PRIMARY KEY,
    date DATE NOT NULL,
    description TEXT,
    merchant TEXT,
    amount NUMERIC(12,2) NOT NULL,
    category TEXT REFERENCES categories(name)
);

CREATE INDEX IF NOT EXISTS idx_transactions_date
ON transactions(date);

CREATE INDEX IF NOT EXISTS idx_transactions_category
ON transactions(category);

INSERT INTO categories (name) VALUES
    ('Food'),
    ('Transport'),
    ('Utilities'),
    ('Entertainment'),
    ('Shopping'),
    ('Other'),
    ('Income'),
    ('Rent')
ON CONFLICT DO NOTHING;

INSERT INTO budgets (category, monthly_limit) VALUES
    ('Food', 8000),
    ('Transport', 3000),
    ('Utilities', 2500),
    ('Entertainment', 3000),
    ('Shopping', 5000),
    ('Other', 2000)
ON CONFLICT (category)
DO UPDATE SET monthly_limit = EXCLUDED.monthly_limit;
