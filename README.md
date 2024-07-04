# Running the Benchmark

To run the benchmark, follow these steps:

1. Ensure all required environment variables are set up for `compose.yaml`. You should make a .env folder at the root of the repo with these variables. We use the `config.py` file to access these variables, and the `.env` file to set them. The `python-dotenv` package is used to load the environment variables from the .env file. These include:
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
   - IMG_NAME ("index.docker.io/username/img:tag")

2. Make the `main.sh` script executable:

   ```
   chmod +x main.sh
   ```

3. Run the `main.sh` script:

   ```
   ./main.sh
   ```

4. Open a new terminal window and run the `benchmark.py` script:

   ```
   python3 benchmark.py --question_types generated_questions user_queries --metrics ctx_relevancy --llms '[{"name": "gpt-4o", "api": "openai", "max_tokens": 1024, "temperature": 0}, {"name": "claude-3-sonnet-20240229", "api": "anthropic", "max_tokens": 1024, "temperature": 0}]' --providers lumina exa google_scholar semantic_scholar lumina_recursive
   ```

## About main.sh

The `main.sh` script performs the following actions:

1. Starts the Docker services defined in `compose.yaml`
2. You can do `docker compose logs` to view the logs of your containers.


## About benchmark.py

The `benchmark.py` script is run separately and performs the actual benchmarking with the following parameters:

- Question types: `generated_questions` and `user_queries`
- Metrics: `ctx_relevancy`
- LLMs: GPT-4, Claude-3 Sonnet, and Claude-3 Haiku
- Providers: Lumina, Exa, Google Scholar, and Semantic Scholar

You can also create your own custom question datasets for benchmarking. Simply add your JSONL file to the `search_benchmark/dataset` folder and use its name (without the .jsonl extension) as a question type when running the benchmark.

### Question Types

The script uses two question types: `generated_questions` and `user_queries`. These correspond to JSONL files located in the `search_benchmark/dataset` folder. Each file contains a set of questions used for the benchmark.

- `generated_questions`: 9k AI-generated questions for benchmarking
- `user_queries`: 9k real user queries from SciSpace for more realistic testing

You can modify these files or add new ones to customize the benchmark according to your needs.
