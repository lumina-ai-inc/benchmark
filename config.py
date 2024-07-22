import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_redis_url():
    load_dotenv()
    return os.getenv('PG_REDIS_URL')
def get_pg_db_name():
    load_dotenv()
    return os.getenv('PG_DB_NAME')
def get_pg_user():
    load_dotenv()
    return os.getenv('PG_USER')
def get_pg_password():
    load_dotenv()
    return os.getenv('PG_PASSWORD')
def get_pg_host():
    load_dotenv()
    return os.getenv('PG_HOST')
def get_pg_port():
    load_dotenv()
    return os.getenv('PG_PORT')
def get_img_url():
    load_dotenv()
    return os.getenv('IMG_URL')
def get_img_name():
    load_dotenv()
    return os.getenv('IMG_NAME')
def get_openai_api_key():
    load_dotenv()
    return os.getenv('OPENAI_API_KEY')
def get_anthropic_api_key():
    load_dotenv()
    return os.getenv('ANTHROPIC_API_KEY')
def get_exa_api_key():
    load_dotenv()
    return os.getenv('EXA_API_KEY')
def get_serp_api_key():
    load_dotenv()
    return os.getenv('SERP_API_KEY')
def get_semantic_scholar_api_key():
    load_dotenv()
    return os.getenv('SEMANTIC_SCHOLAR_API_KEY')
def get_lumina_api_url():
    load_dotenv()
    return os.getenv('API_URL')
def get_exa_url():
    load_dotenv()
    return os.getenv('EXA_URL')
def get_exa_content_url():
    load_dotenv()
    return os.getenv('EXA_CONTENT_URL')