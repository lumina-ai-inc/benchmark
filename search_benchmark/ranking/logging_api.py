import json
import psycopg2
import os
import sys
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)
import concurrent.futures
from search_benchmark.shared.redis_queue import RedisQueue
from search_benchmark.shared.config import get_pg_db_name, get_pg_user, get_pg_password, get_pg_host, get_pg_port

def get_db_connection():
    """
    Creates and returns a new database connection using environment variables.
    """
    db_name = get_pg_db_name()
    user = get_pg_user()
    password = get_pg_password()
    host = get_pg_host()
    port = get_pg_port()
    return psycopg2.connect(dbname=db_name, user=user, password=password, host=host, port=port)

# Listen to the Redis queue 'table_logs'
def listen_to_table_logs():
    queue = RedisQueue('table_logs')
    queue.start_consuming(process_message)

def process_message(message):
    print(f"Processing message from table_logs: {message}")
    try:
        data = json.loads(message)
        table_name = data.get('table')
        payload = data.get('payload')
        
        if not table_name or not payload:
            raise ValueError("Both 'table_name' and 'payload' must be provided in the message.")
        
        # Ensure payload is a JSON string before parsing
        if isinstance(payload, str):
            payload = json.loads(payload)
        
        # Insert the data into the specified table in the database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Assuming the payload is a dictionary of column-value pairs
        columns = ', '.join(payload.keys())
        values = ', '.join(['%s'] * len(payload))
        insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"
        
        cursor.execute(insert_query, list(payload.values()))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        print(f"Data inserted into table {table_name}: {payload}")
    except Exception as e:
        print(f"An error occurred while processing the message: {e}")

# Example usage
if __name__ == "__main__":
    listen_to_table_logs()