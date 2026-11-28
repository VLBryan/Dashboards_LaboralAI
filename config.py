# config.py
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

# Se acepta DB_NAME, LABORAL_DB o ABORAL_DB (typo del .env compartido)
DB_NAME = (
    os.getenv("DB_NAME")
    or os.getenv("LABORAL_DB")
    or os.getenv("ABORAL_DB")
    or "laboral-ai-dev"
)

CACHE_DIR = os.getenv("CACHE_DIR", "./cache")
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "3600"))
MONGO_TIMEOUT_MS = int(os.getenv("MONGO_TIMEOUT_MS", "5000"))
