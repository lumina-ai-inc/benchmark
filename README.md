# A Search Benchmark for Scientific Research 

This repository contains a benchmark for evaluating the performance of different search engines in the context of academic search. We compare, Lumina, Semantic Scholar, Google Scholar, and Exa. This repo requires a `.env` file with API keys for each of these services. 

You will also need a hosted postgres instance to log the benchmark results, and a `redis` instance for communication between the benchmark and the services. We reccomend using `Supabase` for the `postgres` instance, and a managed `redis` instance from `AWS` or `Azure`. You will also need to have `docker` installed to run the benchmark.

NOTE: We have removed recursion from the benchmark code - we have services that include GPUs, to make it easier for general use, we have excluded it from this release.

# Running the Benchmark

To run the benchmark, follow these steps:

1. Ensure all required environment variables are set up for `compose.yaml`. You should make a `.env` file at the root of the repo with these variables. We use the `config.py` file to access these variables, and the `.env` file to set them. The `python-dotenv` package is used to load the environment variables from the .env file. These include:
   - PG_REDIS_URL
   - PG_DB_NAME
   - PG_USER
   - PG_PASSWORD
   - PG_HOST
   - PG_PORT
   - OPENAI_API_KEY
   - ANTHROPIC_API_KEY
   - EXA_API_KEY
   - SERP_API_KEY
   - SEMANTIC_SCHOLAR_API_KEY
   - API_URL
   - EXA_URL ("https://api.exa.ai/search")
   - EXA_CONTENT_URL ("https://api.exa.ai/contents")
   - IMG_URL ("index.docker.io/username/img:tag")
   - IMG_NAME ("username/img:tag")

   NOTE: The IMG_URL and IMG_NAME variables are used to specify the docker image to use for the benchmark, feel free to make your own (`main.sh` has comments to help you do this.).
2. Make the `main.sh` script executable:

   ```
   chmod +x main.sh
   ```

3. Ensure you have docker installed and run the `main.sh` script:

   ```
   ./main.sh
   ```

   This initializes the docker containers and services for the benchmark, which includes the `ranking.py`, `responses.py`, and `logging_api.py` services. Running `main.sh` will build this benchmark into a docker image based on the `IMG_URL` and `IMG_NAME` variables you have provided in the `.env` file.

4. Open a new terminal window and run the `benchmark.py` script from the root dir:

   Install the requirements:
   ```
   python3 -m venv .venv
   source .venv/bin/activate
   pip3 install -r requirements.txt
   ```
   Run the benchmark:
   ```
   python3 benchmark.py
   ```
   You can set the question types, metrics, llms, and providers to run the benchmark with. See the `benchmark.py` file for more details.
   

## About main.sh

The `main.sh` script performs the following actions:

1. Starts the Docker services defined in `compose.yaml` - you can set `replicas` to run more than one instance of each service (provides considerable speedups)
2. You can do `docker compose logs` to view the logs of your containers.


## About benchmark.py

The `benchmark.py` script is run separately and performs the actual benchmarking with the following parameters:

- Question types: `generated_questions` and `user_queries` 
- Metrics: `ctx_relevancy`
- LLMs: Any OpenAI or Anthropic model
- Providers: Lumina, Exa, Google Scholar, and Semantic Scholar

You can also create your own custom question datasets for benchmarking. Simply add your JSONL file to the `search_benchmark/dataset` folder and use its name (without the .jsonl extension) as a question type when running the benchmark.

### Question Types

The script uses two question types: `generated_questions` and `user_queries`. These correspond to JSONL files located in the `search_benchmark/dataset` folder. Each file contains a set of questions used for the benchmark.

- `generated_questions`: 9k AI-generated questions for benchmarking
- `user_queries`: 9k real user queries from SciSpace for more realistic testing

You can modify these files or add new ones to customize the benchmark according to your needs.
