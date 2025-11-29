import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    MODEL_NAME = "gpt-4-turbo-preview"  # or "gpt-3.5-turbo" for cheaper option
    EMBEDDING_MODEL = "text-embedding-3-small"
    
    # Vector DB
    CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
    COLLECTION_NAME = "aurora_memory"
    
    # Chunking
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    
    # Search
    TOP_K_RESULTS = 5
    
    # Temperature settings
    REASONING_TEMPERATURE = 0.7
    SUMMARIZATION_TEMPERATURE = 0.3
