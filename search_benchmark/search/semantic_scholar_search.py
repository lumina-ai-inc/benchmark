import requests
import time
from config import get_semantic_scholar_api_key

def get_paper_data(paper_id):
    time.sleep(1)
    url = f'https://api.semanticscholar.org/graph/v1/paper/{paper_id}'
    paper_data_query_params = {'fields': 'title,abstract'}
    max_retries = 3
    for attempt in range(max_retries):
        response = requests.get(url, params=paper_data_query_params)
        if response.status_code == 200:
            print(f"Retrieved data for paper id: {paper_id}")
            return response.json()
        elif response.status_code == 429:
            print(f"Rate limit exceeded for paper id: {paper_id}. Retrying in 1 second...")
            time.sleep(1)
        else:
            break
    print(f"Failed to retrieve data for paper id: {paper_id} after {max_retries} attempts")
    return None

def fetch_paper_details(question):
    print(f"Question: {question}")
    url = 'https://api.semanticscholar.org/graph/v1/paper/search'
    query_params = {'query': question, 'limit': 10}
    headers = {'x-api-key': get_semantic_scholar_api_key()}
    
    max_retries = 5
    for attempt in range(max_retries):
        response = requests.get(url, params=query_params, headers=headers)
        if response.status_code == 200:
            search_response = response.json()
            print(f"Search response received for question: {question}")
            
            if 'data' in search_response and search_response['data']:
                paper_ids = [paper['paperId'] for paper in search_response['data']]
                paper_details_list = [get_paper_data(paper_id) for paper_id in paper_ids]
                return [details for details in paper_details_list if details]
            else:
                print("No data available in the response.")
                return None
        elif response.status_code == 429:
            print(f"Rate limit exceeded for question: {question}. Retrying in 1 second...")
            time.sleep(1)
        else:
            print(f"Request failed with status code {response.status_code}: {response.text}")
            break
    print(f"Failed to fetch paper details for question: {question} after {max_retries} attempts")
    return None

def process_question(question):
    paper_details_list = fetch_paper_details(question)
    if paper_details_list:
        contexts = [
            {
                "title": paper_details.get('title', 'No title available'),
                "chunks": paper_details.get('abstract', 'No abstract available'),
                "type": "semantic_scholar"
            }
            for paper_details in paper_details_list
        ]
        print(f"Added {len(contexts)} results for question")
    else:
        contexts = [{
            "title": "",
            "chunks": "",
            "type": "semantic_scholar"
        }]
        print("Added empty result for question")
    return contexts

def main(question):
    return process_question(question)

if __name__ == "__main__":
    sample_question = "What are the latest advancements in quantum computing?"
    result = main(sample_question)
    print(result)
