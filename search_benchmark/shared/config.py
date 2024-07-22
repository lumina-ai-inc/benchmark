import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_redis_url():
    return os.getenv('REDIS_URL')

def get_pg_db_name():
    return os.getenv('PG_DB_NAME')

def get_pg_user():
    return os.getenv('PG_USER')

def get_pg_password():
    return os.getenv('PG_PASSWORD')

def get_pg_host():
    return os.getenv('PG_HOST')

def get_pg_port():
    return os.getenv('PG_PORT')

def get_openai_api_key():
    return os.getenv('OPENAI_API_KEY')

def get_anthropic_api_key():
    return os.getenv('ANTHROPIC_API_KEY')

def get_exa_api_key():
    return os.getenv('EXA_API_KEY')

def get_serp_api_key():
    return os.getenv('SERP_API_KEY')

def get_semantic_scholar_api_key():
    return os.getenv('SEMANTIC_SCHOLAR_API_KEY')

def get_lumina_api_url():
    return os.getenv('API_URL')

def get_exa_url():    
    return os.getenv('EXA_URL')

def get_exa_content_url():    
    return os.getenv('EXA_CONTENT_URL')

def get_reranker_url():
    return os.getenv('RERANKER_URL')