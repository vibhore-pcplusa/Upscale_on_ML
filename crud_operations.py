import sqlite3
import logging

logging.basicConfig(filename="app.log", filemode="a",level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CLIENT_DB = "client_db.sqlite"

def create_record(customer_id, amount, date, status):
    """CREATE: Insert a new record into the transactions table."""
    try:
        with sqlite3.connect(CLIENT_DB) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO transactions (customer_id, amount, date, status)
                VALUES (?, ?, ?, ?)
            ''', (customer_id, amount, date, status))
            conn.commit()
            logger.info(f"Created new record with ID: {cursor.lastrowid}")
            return cursor.lastrowid
    except sqlite3.Error as e:
        logger.error(f"Error creating record: {e}")

def read_records():
    """READ: Fetch all records from the transactions table."""
    try:
        with sqlite3.connect(CLIENT_DB) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM transactions')
            rows = cursor.fetchall()
            
            logger.info(f"--- Current Records ({len(rows)}) ---")
            for row in rows:
                logger.info(dict(row))
            logger.info("---------------------------")
    except sqlite3.Error as e:
        logger.error(f"Error reading records: {e}")

def update_record(transaction_id, new_status):
    """UPDATE: Modify the status of an existing transaction."""
    try:
        with sqlite3.connect(CLIENT_DB) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE transactions 
                SET status = ? 
                WHERE id = ?
            ''', (new_status, transaction_id))
            conn.commit()
            
            if cursor.rowcount > 0:
                logger.info(f"Successfully updated transaction ID {transaction_id} to {new_status}")
            else:
                logger.warning(f"No transaction found with ID {transaction_id}")
    except sqlite3.Error as e:
        logger.error(f"Error updating record: {e}")

def delete_record(transaction_id):
    """DELETE: Remove a transaction by its ID."""
    try:
        with sqlite3.connect(CLIENT_DB) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM transactions 
                WHERE id = ?
            ''', (transaction_id,))
            conn.commit()
            
            if cursor.rowcount > 0:
                logger.info(f"Successfully deleted transaction ID {transaction_id}")
            else:
                logger.warning(f"No transaction found with ID {transaction_id}")
    except sqlite3.Error as e:
        logger.error(f"Error deleting record: {e}")

if __name__ == "__main__":
    # 1. READ: Let's see what we currently have
    logger.info("1. Initial Data:")
    read_records()
    
    # 2. CREATE: Add one new record to client_db
    logger.info("\n2. Creating a new record:")
    new_id = create_record(customer_id=104, amount=500.75, date='2023-10-04', status='PENDING')
    
    # 3. READ: Verify it was added
    logger.info("\n3. Data after Creation:")
    read_records()
    
    # 4. UPDATE: Change the status of the record we just added
    logger.info("\n4. Updating the new record:")
    update_record(transaction_id=new_id, new_status='COMPLETED')
    
    # 5. READ: Verify it was updated
    logger.info("\n5. Data after Update:")
    read_records()
    
    # 6. DELETE: (Optional) If you wanted to delete it
    # logger.info("\n6. Deleting the record:")
    # delete_record(transaction_id=new_id)
    # read_records()
