import sqlite3
import os
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()

CLIENT_DB = "client_db.sqlite"
DEST_DB = "destination_db.sqlite"

def reset_databases():
    """Deletes existing databases to start fresh."""
    for db in [CLIENT_DB, DEST_DB]:
        if os.path.exists(db):
            os.remove(db)
            print(f"Deleted {db}")

def create_schema(cursor):
    """Creates the necessary tables in the client database."""
    cursor.execute('''
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            signup_date TEXT,
            risk_score REAL
        )
    ''')
    cursor.execute('''
        CREATE TABLE transactions (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            amount REAL,
            date TEXT,
            status TEXT,
            FOREIGN KEY(customer_id) REFERENCES customers(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE chargebacks (
            id INTEGER PRIMARY KEY,
            transaction_id INTEGER,
            chargeback_date TEXT,
            reason TEXT,
            FOREIGN KEY(transaction_id) REFERENCES transactions(id)
        )
    ''')

def generate_data():
    """Generates scaled mock data using Faker and random."""
    with sqlite3.connect(CLIENT_DB) as conn:
        cursor = conn.cursor()
        create_schema(cursor)
        
        # 1. Generate 200 Customers
        print("Generating 200 Customers...")
        customers = []
        for i in range(1, 201):
            signup_date = fake.date_between(start_date='-2y', end_date='-6m')
            # 10% of customers are high risk (score > 0.8)
            risk_score = random.uniform(0.8, 1.0) if random.random() < 0.1 else random.uniform(0.0, 0.3)
            customers.append((i, fake.name(), fake.email(), signup_date.strftime('%Y-%m-%d'), round(risk_score, 2)))
        
        cursor.executemany('''
            INSERT INTO customers (id, name, email, signup_date, risk_score) 
            VALUES (?, ?, ?, ?, ?)
        ''', customers)
        
        # 2. Generate 500 Transactions
        print("Generating 500 Transactions...")
        transactions = []
        for i in range(1, 501):
            cust = random.choice(customers)
            cust_id = cust[0]
            cust_signup = datetime.strptime(cust[3], '%Y-%m-%d').date()
            
            # Transaction date is after signup
            tx_date = cust_signup + timedelta(days=random.randint(1, 180))
            
            # 5% chance amount is missing (NULL) to test imputation later
            if random.random() < 0.05:
                amount = None
            else:
                # High risk customers tend to have larger transactions
                if cust[4] > 0.8:
                    amount = round(random.uniform(500, 3000), 2)
                else:
                    amount = round(random.uniform(5, 500), 2)
            
            transactions.append((i, cust_id, amount, tx_date.strftime('%Y-%m-%d'), 'COMPLETED'))
            
        cursor.executemany('''
            INSERT INTO transactions (id, customer_id, amount, date, status) 
            VALUES (?, ?, ?, ?, ?)
        ''', transactions)
        
        # 3. Generate 40 Chargebacks (20 Fraud, 20 Non-Fraud)
        print("Generating 40 Chargebacks...")
        chargebacks = []
        # Pick 40 random transactions
        cb_txs = random.sample(transactions, 40)
        
        fraud_reasons = ['Fraudulent transaction', 'Card Stolen']
        non_fraud_reasons = ['Item not received', 'Duplicate charge', 'Unrecognized charge']
        
        for i, tx in enumerate(cb_txs, 1):
            tx_id = tx[0]
            tx_date = datetime.strptime(tx[3], '%Y-%m-%d').date()
            cb_date = tx_date + timedelta(days=random.randint(1, 30))
            
            # First 20 are fraud, last 20 are non-fraud
            if i <= 20:
                reason = random.choice(fraud_reasons)
            else:
                reason = random.choice(non_fraud_reasons)
                
            chargebacks.append((i, tx_id, cb_date.strftime('%Y-%m-%d'), reason))
            
        cursor.executemany('''
            INSERT INTO chargebacks (id, transaction_id, chargeback_date, reason)
            VALUES (?, ?, ?, ?)
        ''', chargebacks)
        
        conn.commit()
        print("Database successfully generated with scaled data!")

if __name__ == "__main__":
    reset_databases()
    generate_data()
