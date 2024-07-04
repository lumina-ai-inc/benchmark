import os
import json
import matplotlib.pyplot as plt
import numpy as np
import sys
from collections import defaultdict

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from search_benchmark.shared.pg import get_db_connection, put_db_connection

def load_results_from_db(run_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    query = """
    SELECT provider, llm, score, question_type, metric
    FROM eval
    WHERE run_id::text = %s
    """
    
    cur.execute(query, (run_id,))
    results = cur.fetchall()

    cur.close()
    put_db_connection(conn)
    
    if not results:
        print(f"No results found for run_id: {run_id}")
    else:
        print(f"Results loaded successfully")
    
    return results

def aggregate_results(results):
    aggregated = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list))))
    for provider, llm, score, question_type, metric in results:
        aggregated[metric][question_type][provider][llm].append(score)
    
    final_results = []
    for metric, question_types in aggregated.items():
        for question_type, providers in question_types.items():
            for provider, llm_scores in providers.items():
                for llm, scores in llm_scores.items():
                    avg_score = sum(scores) / len(scores)
                    final_results.append((metric, question_type, provider, llm, avg_score, len(scores)))
    
    return final_results

def get_providers_and_llms_for_run(run_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT DISTINCT provider, llm, question_type, metric
    FROM eval
    WHERE run_id::text = %s
    """
    
    cursor.execute(query, (run_id,))
    results = cursor.fetchall()
    
    providers = set()
    llms = set()
    question_types = set()
    metrics = set()
    
    for provider, llm, question_type, metric in results:
        providers.add(provider)
        llms.add(llm)
        question_types.add(question_type)
        metrics.add(metric)
    
    cursor.close()
    put_db_connection(conn)
    
    return list(providers), list(llms), list(question_types), list(metrics)

def create_bar_charts(results, run_id):
    providers, llms, question_types, metrics = get_providers_and_llms_for_run(run_id)
    
    # Define the results directory
    results_dir = os.path.join(project_root, 'results')
    os.makedirs(results_dir, exist_ok=True)
    
    for metric in metrics:
        for question_type in question_types:
            filtered_results = [r for r in results if r[0] == metric and r[1] == question_type]
            
            if not filtered_results:
                print(f"No results found for metric: {metric} and question type: {question_type}. Skipping...")
                continue
            fig, ax = plt.subplots(figsize=(15, 10))
            
            x = np.arange(len(providers))
            width = 0.2
            multiplier = 0
            
            for llm, color in zip(llms, plt.cm.viridis(np.linspace(0, 1, len(llms)))):
                offset = width * multiplier
                scores = [next((r[4] for r in filtered_results if r[2] == provider and r[3] == llm), 0) for provider in providers]
                rects = ax.bar(x + offset, scores, width, label=llm, color=color)
                ax.bar_label(rects, fmt='%.2f', padding=3)
                multiplier += 1
            
            ax.set_ylabel(f'Average {metric.capitalize()} Score')
            
            # Get number of questions per provider
            question_counts = [next((r[5] for r in filtered_results if r[2] == provider), 0) for provider in providers]
            
            ax.set_title(f'{metric.capitalize()} Scores by Search Engine and LLM\n'
                         f'(Run ID: {run_id}, Question Type: {question_type}, '
                         f'Total Queries: {sum(question_counts)})')
            ax.set_xticks(x + width * 1.5)
            ax.set_xticklabels([f'{provider}\n({count} questions)' for provider, count in zip(providers, question_counts)])
            ax.legend(loc='upper left', ncol=2)
            ax.set_ylim(0, 1)
            
            plt.tight_layout()
            chart_filename = f'{metric}_comparison_{run_id}_{question_type}.png'
            chart_path = os.path.join(results_dir, chart_filename)
            plt.savefig(chart_path)
            plt.close()
            
            print(f"Bar chart created and saved as '{chart_path}'")

def main(run_id):
    raw_results = load_results_from_db(run_id)
    if not raw_results:
        print("No results to process. Exiting.")
        return
    
    aggregated_results = aggregate_results(raw_results)
    create_bar_charts(aggregated_results, run_id)

if __name__ == "__main__":
    main()