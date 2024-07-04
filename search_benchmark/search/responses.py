import json
import sys
import os
import time

# Get the absolute path to the project root directory
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from search_benchmark.shared.redis_queue import RedisQueue
import search_benchmark.search.lumina_search as lumina_search
import search_benchmark.search.semantic_scholar_search as semantic_scholar_search
import search_benchmark.search.google_scholar_search as google_scholar_search
import search_benchmark.search.exa_search as exa_search
import search_benchmark.search.recursive_search as recursive_search  # Importing recursive_search

def process_search_request(payload):
    question = payload['question']
    providers = payload['providers']
    results = {}

    for provider in providers:
        if provider == 'lumina':
            results['lumina'] = lumina_search.main(question)
        elif provider == 'semantic_scholar':
            results['semantic_scholar'] = semantic_scholar_search.main(question)
        elif provider == 'google_scholar':
            results['google_scholar'] = google_scholar_search.main(question)
        elif provider == 'exa':
            results['exa'] = exa_search.main(question)
        elif provider == 'lumina_recursive':
            results['lumina_recursive'] = recursive_search.main(lumina_search.main, question, recursion_depth=1, page_size=10, page_size_per_recursion=3)  # Using recursive_search for lumina_recursive
        time.sleep(0.05)  # Small sleep after each provider search

    return results

def listen_to_search_queue():
    redis_queue = RedisQueue('search_queue')
    result_queue = RedisQueue('result_queue')

    def callback(body):
        payload = json.loads(body)
        results = process_search_request(payload)
        
        for provider, provider_results in results.items():
            # print(f"Results for provider {provider}: {provider_results}")
            new_payload = {
                'question': payload['question'],
                'results': json.dumps(provider_results),
                'provider': provider,
                'llms': payload['llms'],
                'metrics': payload['metrics'],
                'run_id': payload['run_id'],
                'question_type': payload['question_type']
            }
            
            result_queue.send_to_queue(json.dumps(new_payload))
            time.sleep(0.05)  # Small sleep after sending each result
        
        print(f"Processed question: {payload['question']}")
        print(f"Results sent to result queue for each provider")

    redis_queue.start_consuming(callback)

if __name__ == "__main__":
    listen_to_search_queue()