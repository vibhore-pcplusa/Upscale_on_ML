import nbformat as nbf

nb = nbf.v4.new_notebook()

nb['cells'] = [
    nbf.v4.new_markdown_cell("# Stage 4: Transaction-Level Data Preparation\nThis notebook fulfills the practical deliverable for Stage 4: combining our relational tables into a single flat dataset (one row per transaction) with historical features and a clearly defined outcome label, strictly preventing data leakage."),
    
    nbf.v4.new_markdown_cell("## 1. Connecting to Database"),
    nbf.v4.new_code_cell("""import pandas as pd\nimport sqlite3\n\n# Connect to the destination database\nconn = sqlite3.connect('destination_db.sqlite')\n"""),
    
    nbf.v4.new_markdown_cell("## 2. Feature Engineering & Leakage-Free SQL\nWe will construct a single SQL query that:\n1. Calculates `days_since_signup`.\n2. Uses a Window Function to calculate `previous_transaction_count` (strictly using `ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING` to avoid leakage).\n3. Assigns `is_fraud` = 1 only if the chargeback reason indicates fraud."),
    
    nbf.v4.new_code_cell("""query = '''
SELECT 
    transaction_id,
    transaction_amount,
    customer_risk_score,
    days_since_signup,
    COALESCE(
        COUNT(transaction_id) OVER(
            PARTITION BY customer_id 
            ORDER BY date 
            ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
        ), 0
    ) as previous_transaction_count,
    is_fraud
FROM (
    SELECT 
        t.id as transaction_id,
        t.date,
        c.id as customer_id,
        t.amount as transaction_amount,
        c.risk_score as customer_risk_score,
        CAST(julianday(t.date) - julianday(c.signup_date) AS INTEGER) as days_since_signup,
        COALESCE(MAX(CASE WHEN cb.reason IN ('Fraudulent transaction', 'Card Stolen') THEN 1 ELSE 0 END), 0) as is_fraud
    FROM imported_transactions t
    JOIN imported_customers c ON t.customer_id = c.id
    LEFT JOIN imported_chargebacks cb ON t.id = cb.transaction_id
    GROUP BY t.id
)
ORDER BY date ASC
'''

# Execute the query and load into a pandas DataFrame
df_training = pd.read_sql_query(query, conn)
display(df_training.head(10))
"""),
    
    nbf.v4.new_markdown_cell("## 3. Verification & Validation"),
    nbf.v4.new_code_cell("""# Verify exactly one row per transaction
total_rows = df_training.shape[0]
unique_transactions = df_training['transaction_id'].nunique()

print(f"Total Rows: {total_rows}")
print(f"Unique Transactions: {unique_transactions}")
assert total_rows == unique_transactions, "Error: Multiple rows exist for a single transaction!"
print("✅ Passed: Exactly one row per transaction.")

# Check the label distribution
print("\\nLabel Distribution (is_fraud):")
print(df_training['is_fraud'].value_counts())
"""),
    
    nbf.v4.new_markdown_cell("## 4. Exporting to CSV\nNow that our dataset is verified, we will export it as `training_dataset.csv` for Stage 5 (Modeling)."),
    nbf.v4.new_code_cell("""# Export to CSV without the index column
df_training.to_csv('training_dataset.csv', index=False)
print("Successfully exported to training_dataset.csv!")

# Close the database connection
conn.close()
""")
]

with open('stage4_data_prep.ipynb', 'w') as f:
    nbf.write(nb, f)
print("Stage 4 Notebook created successfully.")
