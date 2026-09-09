import sqlite3
import logging

# Configure logging similarly to your other scripts
logging.basicConfig(
    filename="app.log", 
    filemode="a",
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

CLIENT_DB = "client_db.sqlite"

def setup_additional_tables():
    logger.info("Setting up customers and chargebacks tables.")
    try:
        with sqlite3.connect(CLIENT_DB) as conn:
            cursor = conn.cursor()
            
            # Create Customers table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    email TEXT,
                    signup_date TEXT,
                    risk_score REAL
                )
            ''')
            
            # Create Chargebacks table
            # Includes a foreign key linking back to the transactions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chargebacks (
                    id INTEGER PRIMARY KEY,
                    transaction_id INTEGER,
                    chargeback_date TEXT,
                    reason TEXT,
                    FOREIGN KEY (transaction_id) REFERENCES transactions(id)
                )
            ''')
            
            # Insert 8 records into customers
            customers_data = [
                (101, 'Alice Smith', 'alice@example.com', '2023-01-15', 0.1),
                (102, 'Bob Jones', 'bob@example.com', '2023-02-20', 0.2),
                (103, 'Charlie Brown', 'charlie@example.com', '2023-03-05', 0.05),
                (104, 'Diana Prince', 'diana@example.com', '2023-04-10', 0.8),
                (105, 'Evan Wright', 'evan@example.com', '2023-05-12', 0.15),
                (106, 'Fiona Gallagher', 'fiona@example.com', '2023-06-18', 0.9),
                (107, 'George Lucas', 'george@example.com', '2023-07-22', 0.3),
                (108, 'Hannah Abbott', 'hannah@example.com', '2023-08-30', 0.0)
            ]
            
            # Using REPLACE so you can re-run this script without duplicate key errors
            cursor.executemany('''
                INSERT OR REPLACE INTO customers (id, name, email, signup_date, risk_score)
                VALUES (?, ?, ?, ?, ?)
            ''', customers_data)
            
            # Insert 3 records into chargebacks
            # We reference transaction IDs that we know exist (like 3, 4, 5)
            chargebacks_data = [
                (1, 3, '2023-10-05', 'Fraudulent transaction'),
                (2, 5, '2023-10-08', 'Item not received'),
                (3, 4, '2023-10-09', 'Duplicate charge')
            ]
            
            cursor.executemany('''
                INSERT OR REPLACE INTO chargebacks (id, transaction_id, chargeback_date, reason)
                VALUES (?, ?, ?, ?)
            ''', chargebacks_data)
            
            conn.commit()
            logger.info("Successfully created tables and inserted mock data for customers and chargebacks.")
            
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")

if __name__ == "__main__":
    setup_additional_tables()
    print("Additional tables 'customers' and 'chargebacks' created and populated. Check app.log for details.")
