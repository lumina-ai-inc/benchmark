import openai
import json
import anthropic
import re
from config import get_openai_api_key, get_anthropic_api_key
from typing import List, Dict

CONTEXT_PRECISION_PROMPT = """Given a question and a context, evaluate each sentence in the context for its relevance and criticality in answering the question. 

For each sentence, respond with either '<critical>' or '<not_critical>'. A sentence is critical if it provides unique, indispensable information that directly contributes to answering the question.

Be extremely selective. If there's any doubt about the critical nature of the sentence, mark it as '<not_critical>'.

Respond in the following format:
1. <critical> or <not_critical>
2. <critical> or <not_critical>
3. <critical> or <not_critical>
...

Question: {question}

Context:
{context}"""

def simple_sentence_tokenize(text):
    return re.split(r'(?<=[.!?])\s+', text)

def context_precision_score(question: str, contexts: List[Dict], model: Dict[str, str]) -> float:
    print(f"Starting context precision scoring for question: {question[:30]}...")
    
    if not contexts:
        print("No contexts available. Returning precision score of 0.")
        return 0.0
    
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
    
    max_chars = 50000
    truncated_contexts = []
    current_chars = 0
    
    for context in contexts:
        context_json = json.dumps(context, indent=2)
        if current_chars + len(context_json) <= max_chars:
            truncated_contexts.append(context)
            current_chars += len(context_json)
        else:
            break
    
    print(f"Number of truncated contexts: {len(truncated_contexts)}")
    
    if not truncated_contexts:
        print("No valid contexts after truncation. Returning precision score of 0.")
        return 0.0
    
    context_scores = []
    
    for context in truncated_contexts:
        chunks = context.get('chunks', '')
        if not chunks.strip():
            print("Empty chunks in context. Adding score of 0 for this context.")
            context_scores.append(0.0)
            continue
        
        sentences = simple_sentence_tokenize(chunks)
        total_sentences = len(sentences)
        
        if total_sentences == 0:
            print("No sentences in context. Adding score of 0 for this context.")
            context_scores.append(0.0)
            continue
        
        prompt = CONTEXT_PRECISION_PROMPT.format(
            question=question,
            context=chunks
        )
        
        print(f"Sending request to {model['api']} API...")
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
        
        critical_sentences = len(re.findall(r'<critical>', response_text, re.IGNORECASE))
        context_score = critical_sentences / total_sentences
        context_scores.append(min(context_score, 1.0))  # Ensure the score does not exceed 1
    
    precision_score = sum(context_scores) / len(context_scores) if context_scores else 0.0
    print(f"Computed precision score: {precision_score}")
    return precision_score

def evaluate_context_precision(data_list: List[Dict], api_key: str) -> List[Dict]:
    print(f"Starting evaluation of context precision for {len(data_list)} items...")
    results = []
    for data in data_list:
        question = data["question"]
        results_json = json.loads(data["results"])
        contexts = results_json
        provider = data["provider"]
        llms = data["llms"]

        for model in llms:
            print(f"Processing question: {question[:30]}, provider: {provider}, model: {model['name']}")
            score = context_precision_score(question, contexts, model)
            result = {
                "question": data["question"],
                "provider": data["provider"],
                "model": model["name"],
                "score": score
            }
            results.append(result)
            print(f"Completed evaluation for question: {data['question'][:30]}, provider: {data['provider']}, model: {model['name']}")

    print(f"Completed evaluation of context precision for all items")
    return results

def batch_evaluate_context_precision(data_list: List[Dict], api_key: str) -> List[Dict]:
    print(f"Starting batch evaluation of context precision for {len(data_list)} items...")
    results = evaluate_context_precision(data_list, api_key)
    print(f"Completed batch evaluation of context precision")
    return results