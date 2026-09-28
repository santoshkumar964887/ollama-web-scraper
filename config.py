import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    ollama_host: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "gpt-oss:20b-cloud")
    ollama_timeout: int = int(os.getenv("OLLAMA_TIMEOUT", "120"))
    playwright_timeout: int = int(os.getenv("PLAYWRIGHT_TIMEOUT", "30000"))
    max_content_length: int = int(os.getenv("MAX_CONTENT_LENGTH", "8000"))
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "6000"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "500"))


config = Config()