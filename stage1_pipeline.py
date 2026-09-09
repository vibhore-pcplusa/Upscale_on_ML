import sqlite3
import logging
import os
import sys
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(
    filename="pipeline.log", 
    filemode="a",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

CLIENT_DB = "client_db.sqlite"
DEST_DB = "destination_db.sqlite"

def setup_mock_client_db():
    """Sets up a mock client database with sample data if it doesn't exist."""
    if os.path.exists(CLIENT_DB):
        logger.info(f"Mock client database {CLIENT_DB} already exists.")
        return

    logger.info("Creating mock client database and inserting sample data.")
    try:
        with sqlite3.connect(CLIENT_DB) as conn:
            cursor = conn.cursor()
            # Create a simple table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY,
                    customer_id INTEGER,
                    amount REAL,
                    date TEXT,
                    status TEXT
                )
            ''')
            # Insert some mock records
            mock_data = [
                (1, 101, 250.50, '2023-10-01', 'COMPLETED'),
                (2, 102, 15.00, '2023-10-02', 'COMPLETED'),
                (3, 101, 1200.00, '2023-10-02', 'FAILED'),
                (4, 103, 75.25, '2023-10-03', 'COMPLETED')
            ]
            cursor.executemany('''
                INSERT INTO transactions (id, customer_id, amount, date, status)
                VALUES (?, ?, ?, ?, ?)
            ''', mock_data)
            conn.commit()
            logger.info("Sample data inserted successfully.")
    except sqlite3.Error as e:
        logger.error(f"Error setting up mock client database: {e}")
        sys.exit(1)

def setup_destination_db():
    """Sets up the destination database table."""
    try:
        with sqlite3.connect(DEST_DB) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS imported_transactions (
                    id INTEGER PRIMARY KEY,
                    customer_id INTEGER,
                    amount REAL,
                    date TEXT,
                    status TEXT
                )
            ''')
            conn.commit()
            logger.info("Destination database setup completed.")
    except sqlite3.Error as e:
        logger.error(f"Error setting up destination database: {e}")
        sys.exit(1)

def fetch_records(db_path: str) -> List[Dict[str, Any]]:
    """Fetches records from the specified database."""
    logger.info(f"Fetching records from {db_path}...")
    records = []
    try:
        # Using a context manager for database connection
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row  # To get dict-like rows
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM transactions')
            rows = cursor.fetchall()
            
            # Using list comprehension to convert to standard dictionaries
            records = [dict(row) for row in rows]
            logger.info(f"Successfully fetched {len(records)} records.")
            return records
    except sqlite3.Error as e:
        logger.error(f"Database error while fetching records: {e}")
        raise

def write_records(db_path: str, records: List[Dict[str, Any]]):
    """Writes a list of records to the destination database."""
    if not records:
        logger.warning("No records to write.")
        return

    logger.info(f"Writing {len(records)} records to {db_path}...")
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Use executemany for bulk insert
            # Using REPLACE to handle potential duplicates on repeated runs
            insert_query = '''
                INSERT OR REPLACE INTO imported_transactions (id, customer_id, amount, date, status)
                VALUES (:id, :customer_id, :amount, :date, :status)
            '''
            cursor.executemany(insert_query, records)
            conn.commit()
            logger.info("Records written successfully.")
    except sqlite3.Error as e:
        logger.error(f"Database error while writing records: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise

def main():
    logger.info("Starting pipeline execution.")
    
    # 1. Setup mock databases
    setup_mock_client_db()
    setup_destination_db()
    
    try:
        # 2. Extract
        records = fetch_records(CLIENT_DB)
        
        # 3. Load
        write_records(DEST_DB, records)
        
        logger.info("Pipeline executed successfully.")
        
    except Exception as e:
        logger.critical(f"Pipeline failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
