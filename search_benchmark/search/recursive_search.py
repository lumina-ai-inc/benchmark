from config import get_anthropic_api_key, get_reranker_url
import anthropic
import re
from typing import List, Callable
import json
import requests


def rerank_results(results: List[dict], query: str, batch_size: int = 20):
    def batch(iterable, n=1):
        l = len(iterable)
        for ndx in range(0, l, n):
            yield iterable[ndx:min(ndx + n, l)]

    # Truncate to 350 words
    texts = [' '.join(f"{res['title']} {res['chunks']}".split()[:350])
             for res in results]
    all_index_score_pairs = []
    for result_batch in batch(texts, batch_size):
        payload = {
            "query": query,
            "texts": result_batch,
            "raw_scores": False
        }

        response = requests.post(get_reranker_url(), json=payload)
        response.raise_for_status()
        rerank_results = response.json()

        index_score_pairs = [(item["index"], item["score"])
                             for item in rerank_results]
        all_index_score_pairs.extend(index_score_pairs)

    all_index_score_pairs.sort(key=lambda x: x[1], reverse=True)
    sorted_results = [results[index] for index, _ in all_index_score_pairs]
    return sorted_results


def get_new_questions(question: str, result: dict):
    api_key = get_anthropic_api_key()
    client = anthropic.Anthropic(api_key=api_key)

    prompt = f"""
    Based on the user's query: "{question}", 

    the search result is: 
        {result}

    Identify parts of the user's query that were unanswered or need further refinement, and suggest a refined search query to help find better search results. 
    There should be variation in length, complexity, and specificity across the queries. 
    The query must be based on the detailed concepts, key-terms, hard values and facts in the result you've been provided.
    Wrap it in tags <query>new_query</query>.
    """
    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
        temperature=1
    )
    refined_query = response.content[0].text
    matches = re.findall(r'<query>(.*?)</query>', refined_query, re.DOTALL)
    if matches:
        return [query.strip() for query in matches][:1]
    return []


def recursion_pattern(question: str, results: List[dict]):
    new_questions = []
    results = [{k: v for k, v in res.items() if k != 'type'}
               for res in results]
    for i, result in enumerate(results):
        print(f"Generating new questions for result {i+1} of {len(results)}")
        try:
            llm_questions = get_new_questions(question, result)
            new_questions.extend(llm_questions)
        except Exception as e:
            print(e)
            continue
    print(f"Generated {len(new_questions)} new questions")
    return new_questions


def recursive_search(search_function: Callable, questions: List[str], recursion_depth: int, page_size: int):
    print(f"\n------------------")
    print(f"Recursion depth: {recursion_depth}")
    print(f"------------------")
    new_questions = []
    results = []
    for i, question in enumerate(questions):
        print(f"\nSearching for question {i+1} of {len(questions)}")
        try:
            search_results = search_function(question)[:page_size]
        except Exception as e:
            print(e)
            continue
        results.extend([{**res, 'question': question} for res in search_results])
        new_questions.extend(recursion_pattern(question, search_results))
    if recursion_depth > 1:
        q, r = recursive_search(
            search_function, new_questions, recursion_depth-1, page_size)
        new_questions.extend(q)
        results.extend(r)
    return new_questions, results


def main(search_function: Callable, question: str, recursion_depth: int, page_size: int = 10, page_size_per_recursion: int = 10):
    _, results = recursive_search(
        search_function, [question], recursion_depth, page_size_per_recursion)
    
    # Filter out results with the same chunk
    unique_chunks = set()
    filtered_results = []
    for result in results:
        chunk = result.get('chunks')
        if chunk not in unique_chunks:
            unique_chunks.add(chunk)
            filtered_results.append(result)
    print(f"Filtered {len(results)} results to {len(filtered_results)} unique chunks")
    try:
        reranked_results = rerank_results(filtered_results, question)[:page_size]
    except Exception as e:
        print(e)
        reranked_results = filtered_results[:page_size]
    
    return reranked_results


if __name__ == "__main__":
    from google_scholar_search import main as google_scholar_search
    question = "How does bibliometric analysis help in understanding the impact of a particular research topic?"
    recursion_depth = 1
    page_size = 10
    page_size_per_recursion = 2

    reranked_results = main(
        google_scholar_search, question, recursion_depth, page_size, page_size_per_recursion)
    print(reranked_results)
    with open("reranked_results.json", "w") as f:
        json.dump(reranked_results, f)
