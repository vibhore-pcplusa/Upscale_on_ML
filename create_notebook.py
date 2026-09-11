# pyrefly: ignore [missing-import]
import nbformat as nbf

nb = nbf.v4.new_notebook()

nb['cells'] = [
    nbf.v4.new_markdown_cell("# Stage 2: Data Exploration & Quality Report\nThis notebook fulfills the practical deliverable for Stage 2: identifying missing values, duplicates, unmatched chargebacks, and transaction counts by date using SQL and pandas."),
    
    nbf.v4.new_markdown_cell("## 1. Connecting to Database & Loading Data"),
    nbf.v4.new_code_cell("""import pandas as pd\nimport sqlite3\n\n# Connect to the destination database\nconn = sqlite3.connect('destination_db.sqlite')\n\n# Load tables into pandas DataFrames\ndf_transactions = pd.read_sql_query("SELECT * FROM imported_transactions", conn)\ndf_customers = pd.read_sql_query("SELECT * FROM imported_customers", conn)\ndf_chargebacks = pd.read_sql_query("SELECT * FROM imported_chargebacks", conn)\n\nprint("Transactions shape:", df_transactions.shape)\nprint("Customers shape:", df_customers.shape)\nprint("Chargebacks shape:", df_chargebacks.shape)\n"""),
    
    nbf.v4.new_markdown_cell("## 2. Data Quality Checks\nChecking for missing values, duplicates, and unmatched chargebacks using pandas."),
    nbf.v4.new_code_cell("""# 1. Missing Values\nprint("--- Missing Values ---")\nprint("Transactions:\\n", df_transactions.isnull().sum())\nprint("\\nCustomers:\\n", df_customers.isnull().sum())\nprint("\\nChargebacks:\\n", df_chargebacks.isnull().sum())\n\n# 2. Duplicates (ignoring the primary key 'id' which is always unique)\nprint("\\n--- Duplicate Rows ---")\nprint("Transactions duplicates:", df_transactions.drop(columns=['id']).duplicated().sum())\nprint("Customers duplicates:", df_customers.drop(columns=['id']).duplicated().sum())\nprint("Chargebacks duplicates:", df_chargebacks.drop(columns=['id']).duplicated().sum())\n\n# 3. Unmatched Chargebacks\n# A chargeback is unmatched if its transaction_id doesn't exist in the transactions table\nunmatched = df_chargebacks[~df_chargebacks['transaction_id'].isin(df_transactions['id'])]\nprint("\\n--- Unmatched Chargebacks ---")\nprint(unmatched if not unmatched.empty else "No unmatched chargebacks found.")\n"""),
    
    nbf.v4.new_markdown_cell("## 3. SQL Exploration: Aggregations, Joins, and Window Functions\nWe use `pd.read_sql_query` to run complex SQL directly and load the result into pandas."),
    nbf.v4.new_code_cell("""# Aggregation: Transaction counts by date\nquery_counts = '''\n    SELECT date, COUNT(id) as transaction_count, SUM(amount) as total_amount\n    FROM imported_transactions\n    GROUP BY date\n    ORDER BY date\n'''\ndf_counts = pd.read_sql_query(query_counts, conn)\ndisplay(df_counts)\n"""),
    
    nbf.v4.new_code_cell("""# Joins & Window Functions: Rank customers by their transaction amounts\nquery_window = '''\n    SELECT \n        c.name,\n        t.date,\n        t.amount,\n        RANK() OVER(PARTITION BY c.id ORDER BY t.amount DESC) as amount_rank\n    FROM imported_transactions t\n    JOIN imported_customers c ON t.customer_id = c.id\n'''\ndf_window = pd.read_sql_query(query_window, conn)\ndisplay(df_window)\n"""),
    
    nbf.v4.new_code_cell("""# Close connection when done\nconn.close()\n""")
]

with open('stage2_data_exploration.ipynb', 'w') as f:
    nbf.write(nb, f)
print("Notebook created successfully.")
