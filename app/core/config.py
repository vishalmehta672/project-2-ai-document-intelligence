import os
from dotenv import load_dotenv

load_dotenv()

CELERY_BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")