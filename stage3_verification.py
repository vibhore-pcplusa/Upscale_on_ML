import sqlite3
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CLIENT_DB = "client_db.sqlite"

def update_schema_and_add_data():
    try:
        with sqlite3.connect(CLIENT_DB) as conn:
            cursor = conn.cursor()
            
            # 1. Schema Evolution: Add a new column to client_db.customers
            logger.info("Adding 'phone_number' column to customers table in client_db")
            try:
                cursor.execute('ALTER TABLE customers ADD COLUMN phone_number TEXT')
            except sqlite3.OperationalError:
                # Column might already exist if ran multiple times
                pass
                
            # 2. Insert new records (Incremental Sync test)
            logger.info("Inserting new customer with phone number...")
            cursor.execute('''
                INSERT INTO customers (name, email, signup_date, risk_score, phone_number)
                VALUES ('Ian Wright', 'ian@example.com', '2023-10-15', 0.05, '+1-555-0101')
            ''')
            
            logger.info("Inserting new transaction...")
            cursor.execute('''
                INSERT INTO transactions (customer_id, amount, date, status)
                VALUES (109, 850.00, '2023-10-16', 'COMPLETED')
            ''')
            
            logger.info("Inserting new chargeback...")
            cursor.execute('''
                INSERT INTO chargebacks (transaction_id, chargeback_date, reason)
                VALUES (6, '2023-10-17', 'Card Stolen')
            ''')
            
            conn.commit()
            logger.info("Verification data successfully inserted into client_db.sqlite")
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")

if __name__ == "__main__":
    update_schema_and_add_data()
