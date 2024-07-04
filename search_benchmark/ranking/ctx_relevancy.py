import openai
import json
import anthropic
import re
from config import get_openai_api_key, get_anthropic_api_key
from typing import List, Dict

CONTEXT_RELEVANCE_PROMPT = """Given a question and a single context, determine if this context is absolutely essential and irreplaceable for answering the question. The context contains a 'title', 'chunks', and 'doi'.

Respond with either '<highly_relevant>' or '<not_relevant>'. Base your decision solely on whether the 'chunks' content provides unique, indispensable information that directly answers the question. 

If no context is provided or if the context is empty, respond with '<not_relevant>'. Do not bias any better or worse for length of context. It should not matter.

Question: {question}

Context:
{context}"""

def context_relevancy_score(question: str, contexts: List[Dict], model: Dict[str, str]) -> float:
    print(f"Starting context relevancy scoring for question: {question[:30]}...")
    if model["api"] == "openai":
        api_key = get_openai_api_key()
        client = openai.OpenAI(api_key=api_key)
        print("Using OpenAI API")
    elif model["api"] == "anthropic":
        api_key = get_anthropic_api_key()
        client = anthropic.Anthropic(api_key=api_key)
        print("Using Anthropic API")
    else:
        raise ValueError(f"Unsupported API: {model['api']}")

    print(f"Number of contexts: {len(contexts)}")
    
    highly_relevant_count = 0
    
    for context in contexts:
        prompt = CONTEXT_RELEVANCE_PROMPT.format(
            question=question,
            context=json.dumps(context, indent=2)
        )
        
        print(f"Sending request to {model['api']} API...")
        print(f"Prompt: {prompt}")
        if model["api"] == "openai":
            response = client.chat.completions.create(
                model=model["name"],
                messages=[{"role": "user", "content": prompt}],
                max_tokens=model["max_tokens"],
                n=1,
                stop=None,
                temperature=model["temperature"],
            )
            response_text = response.choices[0].message.content
        elif model["api"] == "anthropic":
            response = client.messages.create(
                model=model["name"],
                max_tokens=model["max_tokens"],
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                temperature=model["temperature"],
            )
            response_text = response.content[0].text
        
        print(f"Response from {model['api']} API: {response_text}")
        
        if '<highly_relevant>' in response_text.lower():
            highly_relevant_count += 1
    
    score = highly_relevant_count / len(contexts) if len(contexts) > 0 else 0
    print(f"Computed score: {score}")
    return score

def evaluate_context_relevancy(data_list: List[Dict], api_key: str) -> List[Dict]:
    print(f"Starting evaluation of context relevancy for {len(data_list)} items...")
    results = []
    for data in data_list:
        question = data["question"]
        results_json = json.loads(data["results"])
        contexts = results_json
        provider = data["provider"]
        llms = data["llms"]

        for model in llms:
            print(f"Processing question: {question[:30]}, provider: {provider}, model: {model['name']}")
            score = context_relevancy_score(question, contexts, model)
            result = {
                "question": data["question"],
                "provider": data["provider"],
                "model": model["name"],
                "score": score
            }
            results.append(result)
            print(f"Completed evaluation for question: {data['question'][:30]}, provider: {data['provider']}, model: {model['name']}")

    print(f"Completed evaluation of context relevancy for all items")
    return results

def batch_evaluate_context_relevancy(data_list: List[Dict], api_key: str) -> List[Dict]:
    print(f"Starting batch evaluation of context relevancy for {len(data_list)} items...")
    results = evaluate_context_relevancy(data_list, api_key)
    print(f"Completed batch evaluation of context relevancy")
    return results
