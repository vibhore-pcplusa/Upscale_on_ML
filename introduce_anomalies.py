import sqlite3
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CLIENT_DB = "client_db.sqlite"

def add_messy_data():
    try:
        with sqlite3.connect(CLIENT_DB) as conn:
            cursor = conn.cursor()
            
            # 1. Missing Values
            # Add transaction with NULL amount and status
            cursor.execute('''
                INSERT INTO transactions (customer_id, amount, date, status)
                VALUES (101, NULL, '2023-10-10', NULL)
            ''')
            # Add customer with NULL email
            cursor.execute('''
                INSERT INTO customers (name, email, signup_date, risk_score)
                VALUES ('Null User', NULL, '2023-10-10', 0.5)
            ''')
            
            # 2. Duplicate Rows
            # Exact duplicate of Alice Smith (minus ID)
            cursor.execute('''
                INSERT INTO customers (name, email, signup_date, risk_score)
                VALUES ('Alice Smith', 'alice@example.com', '2023-01-15', 0.1)
            ''')
            
            # Duplicate chargeback for transaction 3
            cursor.execute('''
                INSERT INTO chargebacks (transaction_id, chargeback_date, reason)
                VALUES (3, '2023-10-05', 'Fraudulent transaction')
            ''')
            
            # 3. Unmatched Chargeback
            # Points to a transaction_id (9999) that doesn't exist in the transactions table
            cursor.execute('''
                INSERT INTO chargebacks (transaction_id, chargeback_date, reason)
                VALUES (9999, '2023-10-11', 'Unrecognized charge')
            ''')
            
            conn.commit()
            logger.info("Messy data successfully introduced into client_db.sqlite")
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")

if __name__ == "__main__":
    add_messy_data()
