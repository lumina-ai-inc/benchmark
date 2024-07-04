import json
import requests
from config import get_lumina_api_url

def query_api(question, page_size: int = 10):
    print(f"Querying API for question: {question}")
    url = f"{get_lumina_api_url()}/search"
    headers = {"Content-Type": "application/json"}
    data = {
        "query": question,
        "dataset_id": "c5bbe32b-4fb7-476a-81aa-fe269f67f283",
        "page": 1,
        "filters": {"must": None, "must_not": None, "should": None},
        "page_size": page_size,
        "group_size": 3,
        "search_type": "hybrid",
        "slim_chunks": False,
        "highlight_results": True,
        "highlight_threshold": 0.8,
        "highlight_delimiters": ["?", ".", "!"],
        "highlight_max_length": 20,
        "highlight_max_num": 4,
        "recency_bias": 3,
        "get_total_pages": False,
        "score_threshold": 0,
        "get_collisions": True
    }
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        try:
            print("API query successful")
            return response.json()
        except requests.exceptions.JSONDecodeError:
            print(f"Error: Unable to decode JSON. Response content: {response.text}")
            return None
    else:
        print(f"Error: API request failed with status code {response.status_code}. Response content: {response.text}")
        return None

def process_results_lumina(results):
    print("Processing Lumina results")
    processed_results = []
    doi = ""
    for group_chunk in results['group_chunks']:
        group_name = group_chunk['group_name']
        group_data = {"title": group_name, "chunks": "", "doi": doi, "type": "lumina"}
        for chunk in group_chunk['metadata']:
            metadata = chunk['metadata'][0]
            doi = metadata['metadata']['doi']
            content_html = metadata['chunk_html']
            if content_html != doi:
                group_data["chunks"] += content_html
            group_data["doi"] = doi
        processed_results.append(group_data)
    print(f"Processed {len(processed_results)} results")
    return processed_results

def get_abstract(group_tracking_id):
    print(f"Fetching abstract for group_tracking_id: {group_tracking_id}")
    url = f"{get_lumina_api_url()}/file/{group_tracking_id}"
    response = requests.get(url)
    if response.status_code == 200:
        file_metadata = response.json()
        abstract = file_metadata.get('abstract', None)
        print("Abstract fetched successfully" if abstract else "No abstract found")
        return abstract
    else:
        print(f"Failed to fetch abstract. Status code: {response.status_code}")
        return None

def process_results_lumina_abstracts(results):
    print("Processing Lumina results with abstracts")
    processed_results = []
    for group_chunk in results['group_chunks']:
        group_name = group_chunk['group_name']
        group_tracking_id = group_chunk['group_tracking_id']
        group_data = {"title": group_name, "chunks": "", "doi": "", "type": "lumina"}

        abstract = get_abstract(group_tracking_id)
        if abstract:
            group_data["chunks"] = abstract
            for chunk in group_chunk['metadata']:
                metadata = chunk['metadata'][0]
                doi = metadata['metadata']['doi']
                group_data["doi"] = doi
                if group_data["doi"]:
                    break
        else:
            print("No abstract found, processing chunks")
            for chunk in group_chunk['metadata']:
                metadata = chunk['metadata'][0]
                doi = metadata['metadata']['doi']
                content_html = metadata['chunk_html']
                group_data["chunks"] += content_html
                group_data["doi"] = doi

        processed_results.append(group_data)
    print(f"Processed {len(processed_results)} results with abstracts")
    return processed_results

def process_question(question, type='full', page_size=10):
    print(f"Processing question: {question}")
    results = query_api(question, page_size=page_size)
    if results is None:
        print("No results found for the question")
        return []
    if type == 'full':
        return process_results_lumina(results)
    else:
        return process_results_lumina_abstracts(results)

def main(question, type='full'):
    print(f"Processing question: {question}")
    results = process_question(question)
    return results


if __name__ == "__main__":
    question = "What is the role of mitochondria in cellular energy production?"
    results = main(question)
    print(json.dumps(results, indent=2))

