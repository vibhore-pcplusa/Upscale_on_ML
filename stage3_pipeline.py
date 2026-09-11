import sqlite3
import logging
import os
import sys
from typing import List, Dict, Any
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Load environment variables securely from .env file
load_dotenv()

CLIENT_DB = os.getenv("CLIENT_DB_PATH")
DEST_DB = os.getenv("DEST_DB_PATH")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", 100))

# Configure logging
logging.basicConfig(
    filename="pipeline_stage3.log", 
    filemode="a",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Verify configurations
if not CLIENT_DB or not DEST_DB:
    logger.critical("Database paths not found in environment variables.")
    sys.exit(1)

# Retry decorator for robust database connection/operations
@retry(
    stop=stop_after_attempt(3), 
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(sqlite3.OperationalError)
)
def execute_query_with_retry(db_path: str, query: str, params: tuple = (), fetch: bool = False, fetch_size: int = None):
    """Executes a query with built-in retries for OperationalErrors (like locks)."""
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query, params)
        if fetch:
            if fetch_size:
                return cursor.fetchmany(fetch_size)
            return cursor.fetchall()
        conn.commit()

def setup_checkpoints_table():
    """Sets up the pipeline_checkpoints table to track incremental loads."""
    query = '''
        CREATE TABLE IF NOT EXISTS pipeline_checkpoints (
            table_name TEXT PRIMARY KEY,
            last_synced_id INTEGER
        )
    '''
    execute_query_with_retry(DEST_DB, query)
    logger.info("Checkpoint table setup completed.")

def get_last_synced_id(table_name: str) -> int:
    """Retrieves the last synced ID for a given table from checkpoints."""
    query = "SELECT last_synced_id FROM pipeline_checkpoints WHERE table_name = ?"
    result = execute_query_with_retry(DEST_DB, query, (table_name,), fetch=True)
    if result:
        return result[0]['last_synced_id']
    return 0

def update_checkpoint(table_name: str, last_id: int):
    """Updates the checkpoint table with the newly synced maximum ID."""
    query = '''
        INSERT OR REPLACE INTO pipeline_checkpoints (table_name, last_synced_id)
        VALUES (?, ?)
    '''
    execute_query_with_retry(DEST_DB, query, (table_name, last_id))

def evolve_schema(dest_table: str, source_record: Dict[str, Any]):
    """Checks for new columns in source data and alters the destination table if needed."""
    # Get current columns in destination table
    with sqlite3.connect(DEST_DB) as conn:
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({dest_table})")
        existing_columns = {row[1] for row in cursor.fetchall()}
    
    # Check if the source record has any keys not in the destination table
    for column in source_record.keys():
        if column not in existing_columns:
            logger.info(f"Schema Evolution: Adding new column '{column}' to '{dest_table}'")
            # In production, we'd map types carefully. Here we'll default to TEXT.
            try:
                execute_query_with_retry(DEST_DB, f"ALTER TABLE {dest_table} ADD COLUMN {column} TEXT")
                existing_columns.add(column)
            except sqlite3.OperationalError as e:
                logger.error(f"Failed to alter schema for {dest_table}: {e}")

@retry(
    stop=stop_after_attempt(3), 
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(sqlite3.OperationalError)
)
def write_batch(dest_table: str, batch: List[sqlite3.Row]) -> int:
    """Writes a batch of records to the destination table and returns the max ID."""
    if not batch:
        return 0
        
    records = [dict(row) for row in batch]
    
    # 1. Handle potential Schema Evolution based on the first record in the batch
    evolve_schema(dest_table, records[0])
    
    # 2. Build and execute dynamic INSERT
    columns = ', '.join(records[0].keys())
    placeholders = ', '.join([':' + key for key in records[0].keys()])
    
    insert_query = f'''
        INSERT OR REPLACE INTO {dest_table} ({columns})
        VALUES ({placeholders})
    '''
    
    with sqlite3.connect(DEST_DB) as conn:
        cursor = conn.cursor()
        cursor.executemany(insert_query, records)
        conn.commit()
    
    # Return the maximum ID from this batch to update the checkpoint
    return max(record['id'] for record in records)

def process_table_incrementally(source_table: str, dest_table: str):
    """Extracts, transforms, and loads a table incrementally using batching."""
    last_id = get_last_synced_id(source_table)
    logger.info(f"Starting incremental sync for {source_table} (ID > {last_id})")
    
    # Open a dedicated connection to fetch the data in batches
    with sqlite3.connect(CLIENT_DB) as source_conn:
        source_conn.row_factory = sqlite3.Row
        source_cursor = source_conn.cursor()
        
        # Order by ID is crucial for reliable checkpoints
        query = f"SELECT * FROM {source_table} WHERE id > ? ORDER BY id ASC"
        source_cursor.execute(query, (last_id,))
        
        total_synced = 0
        max_id_synced = last_id
        
        while True:
            batch = source_cursor.fetchmany(BATCH_SIZE)
            if not batch:
                break
                
            # Write the batch
            batch_max_id = write_batch(dest_table, batch)
            if batch_max_id > max_id_synced:
                max_id_synced = batch_max_id
                
            total_synced += len(batch)
            logger.info(f"  ...synced batch of {len(batch)} records for {source_table}.")
        
        # Update checkpoint if we synced anything
        if total_synced > 0:
            update_checkpoint(source_table, max_id_synced)
            logger.info(f"Finished sync for {source_table}: {total_synced} total records inserted. New checkpoint ID: {max_id_synced}")
        else:
            logger.info(f"Finished sync for {source_table}: No new records found.")

def main():
    logger.info("=== Starting Stage 3 Pipeline Execution ===")
    
    setup_checkpoints_table()
    
    tables_to_sync = {
        'transactions': 'imported_transactions',
        'customers': 'imported_customers',
        'chargebacks': 'imported_chargebacks'
    }
    
    try:
        for source_table, dest_table in tables_to_sync.items():
            process_table_incrementally(source_table, dest_table)
            
        logger.info("=== Pipeline executed successfully ===")
        
    except Exception as e:
        logger.critical(f"Pipeline failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
