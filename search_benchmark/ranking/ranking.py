import json
import sys
import os
import time
import uuid
from datetime import datetime
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)
import concurrent.futures
from search_benchmark.shared.redis_queue import RedisQueue
from search_benchmark.ranking.ctx_relevancy import batch_evaluate_context_relevancy
from search_benchmark.ranking.ctx_precision import batch_evaluate_context_precision
from search_benchmark.ranking.config import get_openai_api_key, get_anthropic_api_key
from search_benchmark.shared.pg import get_db_connection, put_db_connection


def create_eval_table_if_not_exists():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS eval (
                    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
                    run_id UUID NOT NULL,
                    question TEXT,
                    metric TEXT,
                    results TEXT,
                    score NUMERIC,
                    provider TEXT,
                    llm TEXT,
                    question_type TEXT
                )
            """)
        conn.commit()
    except Exception as e:
        conn.rollback()
    finally:
        put_db_connection(conn)

def send_eval_row_to_redis(eval_row):

    table_logs_queue = RedisQueue('table_logs')
    try:
        log_data = {
            'table': 'eval',
            'payload': eval_row
        }
        table_logs_queue.send_to_queue(json.dumps(log_data))
    except Exception as e:
        print(f"Error sending eval row to Redis queue: {e}")

def process_batch(batch):

    data_list = []
    for payload in batch:
        print(f"Debug: Processing payload: {payload}")
        question = payload['question']
        results = payload['results']
        provider = payload['provider']
        llms = payload['llms']
        question_type = payload['question_type']
        metrics = payload['metrics']
        data_list.append({
            'question': question,
            'results': results,
            'provider': provider,
            'llms': llms,
            'question_type': question_type,
            'metrics': metrics
        })

    api_key = get_openai_api_key() if 'openai' in [llm['api'] for data in data_list for llm in data['llms']] else get_anthropic_api_key()
    
    try:
        for metric in data_list[0]['metrics']:
            print(f"Debug: Processing metric: {metric}")
            if metric == 'ctx_precision':
                scores = batch_evaluate_context_precision(data_list, api_key)
            else:
                scores = batch_evaluate_context_relevancy(data_list, api_key)

            for score_data in scores:
                print(f"Debug: Processing score data: {score_data}")
                eval_row = {
                    'run_id': str(payload['run_id']),
                    'question': score_data['question'],
                    'metric': metric,
                    'results': json.dumps(results),
                    'score': score_data['score'],
                    'provider': score_data['provider'],
                    'llm': str(score_data['model']),
                    'question_type': payload['question_type']
                }
                try:
                    send_eval_row_to_redis(eval_row)
                except Exception as e:
                    print(f"Error sending eval row to Redis: {e}")

        print(f"Processed batch of {len(batch)} results")
    except Exception as e:
        print(f"Error processing batch: {e}")

def listen_to_result_queue(batch_size=1):

    result_queue = RedisQueue('result_queue')
    batch = []

    def callback(body):
        nonlocal batch
        print("Debug: Callback function called")
        payload = json.loads(body)
        batch.append(payload)

        
        if len(batch) >= batch_size:
            process_batch(batch)
            batch = []

    result_queue.start_consuming(callback)

def main():
    print("Starting ranking process...")
    create_eval_table_if_not_exists()
    listen_to_result_queue()
    print("Ranking process completed.")

if __name__ == "__main__":
    print("Debug: Script started")
    main()
    print("Debug: Script finished")
