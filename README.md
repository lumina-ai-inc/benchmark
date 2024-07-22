# An Open Source Evaluation for Search APIs

This repository presents a comprehensive benchmark designed to evaluate the performance of various search engines in the academic research domain. We specifically compare Lumina, Semantic Scholar, Google Scholar, and Exa, focusing on two key metrics: Context Relevance and Context Precision. By employing large language models (LLMs) as evaluators, we assess the quality of search results provided by each engine, ensuring a robust analysis of their effectiveness in delivering relevant and precise information to researchers.

This repo requires a `.env` file with API keys for each of these services. 

We setup a local `postgres` instance to log the benchmark results, and a local `redis` instance for communication between the benchmark and the services. To run the benchmark with recursion, you will need to host a `reranker` service. We use the BGE Large raranker. By default this is turned off. 

You can pull and build the benchmark image from dockerhub with the following command from the root dir of the project:
```
./docker.sh
```
# Components

## `.env`

 We set up API keys, postgres and redis and config for the benchmark in this file. You should make a `.env` file at the root of the repo with these variables. We use the `config.py` file to access these variables, and the `.env` file to set them. The `python-dotenv` package is used to load the environment variables from the .env file. These include:

   - REDIS_URL
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
   - API_URL (for lumina)
   - EXA_URL ("https://api.exa.ai/search")
   - EXA_CONTENT_URL ("https://api.exa.ai/contents")
   - IMG_URL ("index.docker.io/username/img:tag")
   - IMG_NAME ("username/img:tag")
   - RERANKER_URL (host a reranker if you want to do recursive search)
   - QUESTION_TYPES=user_queries,generated_questions
   - METRICS=ctx_relevancy, ctx_precision
   - LLMS=[{"name": "gpt-4o", "api": "openai", "max_tokens": 1024, "temperature": 0}, {"name": "claude-3-haiku-20240307", "api": "anthropic", "max_tokens": 1024, "temperature": 0}]
   - PROVIDERS=lumina,google_scholar,semantic_scholar,exa
   - NUM_Q=500

   (if you want recursion add a "-recursive" to the end of the provider name, like lumina_recursive,google_scholar_recursive,semantic_scholar_recursive)

## `compose.yaml`

The `compose.yaml` file orchestrates the deployment of all services required for the benchmark. It defines the configuration for each service, including dependencies, environment variables, and the number of replicas to run. This setup allows for efficient communication between the benchmark and the various search providers, as well as logging and data storage through Redis and PostgreSQL.

- **logging_api**: Handles logging of benchmark results and depends on Redis and PostgreSQL for data storage.
- **questions**: Runs the benchmark process, sending questions to the configured providers and processing their responses.
- **responses**: Manages the responses from the search providers, processing and storing the results.
- **ranking**: Responsible for ranking the responses received from the providers based on the defined metrics.
- **redis**: Provides a Redis instance for message queuing and inter-service communication.
- **pg**: Sets up a PostgreSQL database for logging benchmark results and storing relevant data.
- **adminer**: A web-based database management tool for interacting with the PostgreSQL database.

This setup allows for efficient benchmarking and evaluation of different search APIs.
## benchmark.py

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

You don't need to run all questions, you can specifiy num questions in the `benchmark.py` file.
You can modify these files or add new ones to customize the benchmark according to your needs.

# Running the Benchmark

   1. Set environment variables in .env in root of project.

   2. pull the benchmark image from dockerhub with:
   ```
    ./docker.sh 
   ```
   3. Run `docker compose up -d` to start the benchmark. This will start all of the services defined in the `compose.yaml` file.

   ```
      docker compose up -d 
   ```
   4. Run `docker compose logs -f questions`. This will print a Streamlit link to the benchmark dashboard to view progress.

   5. To stop the benchmark, run `docker compose down`.
