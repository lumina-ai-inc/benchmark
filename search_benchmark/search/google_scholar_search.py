import requests
import json
from config import get_serp_api_key

def fetch_google_scholar_results(question):
    url = "https://serpapi.com/search"
    params = {
        "engine": "google_scholar",
        "q": question,
        "api_key": get_serp_api_key()
    }
    response = requests.get(url, params=params)
    results = response.json()
    return results

def process_google_scholar_results(results):
    processed_results = []
    for result in results.get('organic_results', []):
        processed_results.append({
            "title": result.get('title', 'No title available'),
            "chunks": result.get('snippet', 'No content available'),
            "type": "google_scholar"
        })
    print(f"Processed {len(processed_results)} results")
    return processed_results

def main(question):
    results = fetch_google_scholar_results(question)
    if results:
        processed_results = process_google_scholar_results(results)
        return (processed_results)
    print("No results found")
    return None

if __name__ == "__main__":
    sample_question = "What are the effects of climate change on biodiversity?"
    print(f"Running sample search with question: {sample_question}")
    result = main(sample_question)
    print("Final result:")
    print(result)
