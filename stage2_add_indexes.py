import sqlite3
import logging

logging.basicConfig(
    filename="pipeline.log", 
    filemode="a",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

DEST_DB = "destination_db.sqlite"

def add_indexes():
    logger.info("Adding indexes to destination_db.sqlite for Stage 2 exploration.")
    try:
        with sqlite3.connect(DEST_DB) as conn:
            cursor = conn.cursor()
            
            # Indexes for imported_transactions
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_customer_id ON imported_transactions(customer_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_date ON imported_transactions(date)')
            
            # Indexes for imported_customers
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_customers_email ON imported_customers(email)')
            
            # Indexes for imported_chargebacks
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_chargebacks_transaction_id ON imported_chargebacks(transaction_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_chargebacks_date ON imported_chargebacks(chargeback_date)')
            
            conn.commit()
            logger.info("Successfully added indexes to destination_db.sqlite.")
    except sqlite3.Error as e:
        logger.error(f"Database error while adding indexes: {e}")

if __name__ == "__main__":
    add_indexes()
