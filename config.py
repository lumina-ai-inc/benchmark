import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_redis_url():
    return os.environ.get('PG_REDIS_URL')
def get_pg_db_name():
    return os.environ.get('PG_DB_NAME')
def get_pg_user():
    return os.environ.get('PG_USER')
def get_pg_password():
    return os.environ.get('PG_PASSWORD')
def get_pg_host():
    return os.environ.get('PG_HOST')
def get_pg_port():
    return os.environ.get('PG_PORT')
def get_img_url():
    return os.environ.get('IMG_URL')
def get_img_name():
    return os.environ.get('IMG_NAME')
def get_openai_api_key():
    return os.environ.get('OPENAI_API_KEY')
def get_anthropic_api_key():
    return os.environ.get('ANTHROPIC_API_KEY')
def get_exa_api_key():
    return os.environ.get('EXA_API_KEY')
def get_serp_api_key():
    return os.environ.get('SERP_API_KEY')
def get_semantic_scholar_api_key():
    return os.environ.get('SEMANTIC_SCHOLAR_API_KEY')
def get_lumina_api_url():
    return os.environ.get('API_URL')
def get_exa_url():
    return os.environ.get('EXA_URL')
def get_exa_content_url():
    return os.environ.get('EXA_CONTENT_URL')