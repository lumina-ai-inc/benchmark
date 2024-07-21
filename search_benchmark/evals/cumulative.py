import streamlit as st
import sys
import os
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

load_dotenv()

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from search_benchmark.evals.graphing import load_results_from_db, aggregate_results

def generate_cumulative_charts():
    st.title("Cumulative Search Benchmark Evaluation")

    # Load all results from the database
    all_results = load_results_from_db(run_id=None)  # Pass None to get all results
    
    if all_results:
        st.info(f"Raw results loaded: {len(all_results)} entries")
        
        # Filter results for specific providers, and exclude scores > 1
        filtered_results = [
            result for result in all_results 
            if result[0] in ['exa', 'lumina', 'lumina_recursive', 'semantic_scholar', 'google_scholar'] and
            result[2] <= 1
        ]
        
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(filtered_results, columns=['provider', 'llm', 'score', 'question_type', 'metric'])
        
        # Group by metric and provider, then calculate mean score across all LLMs
        aggregated_results = df.groupby(['metric', 'provider'])['score'].mean().reset_index()
        
        st.info(f"Aggregated results: {len(aggregated_results)} entries")
        
        # Create and display bar charts
        metrics = aggregated_results['metric'].unique()
        providers = aggregated_results['provider'].unique()
        
        for metric in metrics:
            plt.figure(figsize=(12, 6))
            
            metric_data = aggregated_results[aggregated_results['metric'] == metric]
            
            sns.barplot(x='provider', y='score', data=metric_data)
            plt.title(f'Average {metric.capitalize()} Scores Across Providers (All LLMs)')
            plt.xlabel('Provider')
            plt.ylabel('Average Score')
            plt.xticks(rotation=45)
            
            st.pyplot(plt)
            plt.close()

    else:
        st.error("No results found in the database.")

if __name__ == "__main__":
    generate_cumulative_charts()
