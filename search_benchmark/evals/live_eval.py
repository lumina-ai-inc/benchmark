import streamlit as st
import sys
import os
import argparse
from dotenv import load_dotenv

load_dotenv()

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from search_benchmark.evals.graphing import load_results_from_db, aggregate_results, create_bar_charts

def generate_charts(run_id):
    if run_id:
        st.info(f"Generating charts for Run ID: {run_id}")
        # Load results from the database
        raw_results = load_results_from_db(run_id)
        
        if raw_results:
            st.info(f"Raw results loaded: {len(raw_results)} entries")
            # Aggregate the results
            aggregated_results = aggregate_results(raw_results)
            st.info(f"Aggregated results: {len(aggregated_results)} entries")
            
            # Create and display bar charts
            create_bar_charts(aggregated_results, run_id)
            
            # Display the generated charts
            st.subheader("Generated Charts")
            
            # Get the list of generated chart files
            results_dir = os.path.join(project_root, 'results')
            print(results_dir)
            st.info(f"Looking for charts in: {results_dir}")
            chart_files = [f for f in os.listdir(results_dir) if f".png" in f and run_id in f]
            st.info(f"Found {len(chart_files)} chart files")
            
            if chart_files:
                for chart_file in chart_files:
                    chart_path = os.path.join(results_dir, chart_file)
                    st.image(chart_path, caption=chart_file, use_column_width=True)
                
                st.success(f"{len(chart_files)} chart(s) displayed successfully!")
            else:
                st.warning("No charts were found for the given Run ID.")
        else:
            st.error("No results found for the given Run ID.")
    else:
        st.warning("Please enter a Run ID.")

def main():
    st.title("Search Benchmark Evaluation")

    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--run_id", type=str, help="Run ID to use")
    args = parser.parse_args()

    # Input for run ID, with default value from command-line argument
    run_id = st.text_input("Enter Run ID:", value=args.run_id if args.run_id else "")

    # Generate Charts button
    if st.button("Generate Charts"):
        generate_charts(run_id)

    # Refresh button
    if st.button("Refresh"):
        generate_charts(run_id)

if __name__ == "__main__":
    main()