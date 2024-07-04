import json
import requests
from exa_py import Exa
from config import get_exa_api_key, get_exa_url, get_exa_content_url

exa = Exa(api_key=get_exa_api_key())

def search_exa(question):
    url = "https://api.exa.ai/search"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "x-api-key": get_exa_api_key()
    }
    payload = {"query": question}
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Request failed with status code {response.status_code}: {response.text}")
        return None

def get_content_from_exa(url):
    print(f"Getting content for URLs: {url}")
    try:
        results = exa.get_contents([url])
        # print(f"Content Results: {results}")
        return [result.text if result else '' for result in results.results]
    except ValueError as e:
        print(f"Error fetching content for URLs: {str(e)}")
        return "No Content"

def process_exa_results(results):
    print("Processing Exa results")
    processed_results = []
    
    for result in results:
        # print(f"Result: {result}")
        url = result.get('url', '')
        content = get_content_from_exa(url)
        # print(f"Content: {content}")

        content_data = str(content)
        # print(f"Content data: {content_data}")
        # print(f"Chunks: {chunks}")
        processed_result = {
            "title": result.get('title', 'No title available'),
            "chunks": content_data,
            "type": "exa"
        }
        processed_results.append(processed_result)
    
    # print(f"Processed {processed_results} results")
    return processed_results

def main(question):
    print(f"Processing question: {question}")
    exa_results = search_exa(question)

    if exa_results and 'results' in exa_results:
        exa_results_list = exa_results['results']
    else:
        print("No results found or unexpected response structure from Exa API")
        return []
    # print(f"Exa results: {exa_results}")
    
    processed_results = process_exa_results(exa_results_list)
    
    return processed_results

if __name__ == "__main__":
    question = "What are the latest advancements in quantum computing?"
    results = main(question)
    print("Results:", results)

