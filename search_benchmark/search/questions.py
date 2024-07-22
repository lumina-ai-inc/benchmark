import os
import json
import uuid
import sys
import time
import dotenv
dotenv.load_dotenv()
# Get the absolute path to the project root directory
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from search_benchmark.shared.redis_queue import RedisQueue
from config import get_redis_url

def main(question_type, metrics, llms, providers, run_id, num_q=0):
    questions_file = os.path.join(project_root, 'search_benchmark', 'dataset', f'{question_type}.jsonl')
    print(f"Loading questions from file: {questions_file}")

    # Ensure the data directory exists
    data_dir = os.path.join(project_root, 'data')
    os.makedirs(data_dir, exist_ok=True)
    print(f"Data directory ensured at: {data_dir}")

    # Initialize Redis queue
    redis_queue = RedisQueue('search_queue', get_redis_url())
    print("Initialized Redis queue.", get_redis_url())

    # Read questions from file
    with open(questions_file, 'r') as f:
        questions = [json.loads(line)['question'] for line in f]  # Limit to first 200 questions
    print(f"Loaded {len(questions)} questions.")

    # Process each question
    questions_to_process = questions[:num_q] if num_q != 0 else questions
    print(f"Processing {len(questions_to_process)} questions.")
    
    for question in questions_to_process:
        payload = {
            'question': question,
            'metrics': metrics,
            'llms': llms,
            'providers': providers,
            'run_id': run_id,
            'question_type': question_type
        }
        
        # Send payload to Redis queue
        redis_queue.send_to_queue(json.dumps(payload))
        print(f"Sent question to Redis queue: {question}")

        # Add a small sleep after sending each question
        time.sleep(0.001)


if __name__ == "__main__":
    # Example usage
    question_types = ['generated_questions', 'user_queries']
    metrics = ['ctx_relevancy']
    llms = [
        {"name": "gpt-4o", "api": "openai", "max_tokens": 1024, "temperature": 0}
        # {"name": "claude-3-sonnet-20240229", "api": "anthropic", "max_tokens": 1024, "temperature": 0},
        # {"name": "claude-3-haiku-20240307", "api": "anthropic", "max_tokens": 1024, "temperature": 0}
    ]
    providers = ['lumina', 'google_scholar', 'semantic_scholar']
    # providers = ['lumina_recursive']
    run_id = str(uuid.uuid4())

    for question_type in question_types:
        main(question_type, metrics, llms, providers, run_id, num_q=300)
