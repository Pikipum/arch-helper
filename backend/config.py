import os
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.getenv("DB_PATH", "../chromadb")
))
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "arch_wiki")
MODEL_NAME = os.getenv("MODEL_NAME", "mistral")
RETRIEVAL_K = int(os.getenv("RETRIEVAL_K", "4"))
RETRIEVAL_CANDIDATES = RETRIEVAL_K * 4
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")