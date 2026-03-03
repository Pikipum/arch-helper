# Settings for model name etc

import os

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "chromadb"))
COLLECTION_NAME = "arch_wiki"
MODEL_NAME = "mistral"
RETRIEVAL_K = 4
CORS_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
]