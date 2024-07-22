import os
import sys
import uuid
import subprocess
import argparse
import json
from dotenv import load_dotenv

load_dotenv()

# Get the absolute path to the project root directory
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from search_benchmark.search.questions import main as process_questions
from config import get_question_types, get_metrics, get_llms, get_providers

def run_benchmark(question_types, metrics, llms, providers):
    # Generate a unique run ID
    run_id = str(uuid.uuid4())
    print(f"Run ID: {run_id}")
    print("SENDING QUESTIONS")
    # Process questions for each question type
    for question_type in question_types:
        process_questions(question_type, metrics, llms, providers, run_id, num_q=500)
    
    # Run the Streamlit app
    streamlit_path = os.path.join(project_root, 'search_benchmark', 'evals', 'live_eval.py')
    print(f"Attempting to run Streamlit app at: {streamlit_path}")
    if os.path.exists(streamlit_path):
        subprocess.run(['streamlit', 'run', streamlit_path, '--', f'--run_id={run_id}'])
    else:
        print(f"Error: The file {streamlit_path} does not exist.")

if __name__ == "__main__":
    # Define default values from config
    default_question_types = get_question_types()
    default_metrics = get_metrics()
    default_llms = get_llms()
    default_providers = get_providers()

    # Set up argument parser
    parser = argparse.ArgumentParser(description="Run benchmark with specified parameters")
    parser.add_argument("--question_types", nargs="+", default=default_question_types, help="List of question types")
    parser.add_argument("--metrics", nargs="+", default=default_metrics, help="List of metrics")
    parser.add_argument("--llms", type=json.loads, default=default_llms, help="JSON string of LLM configurations")
    parser.add_argument("--providers", nargs="+", default=default_providers, help="List of providers")

    # Parse arguments
    args = parser.parse_args()

    # Run benchmark with parsed arguments
    run_benchmark(args.question_types, args.metrics, args.llms, args.providers)