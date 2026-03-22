from functools import lru_cache
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent.parent.parent / ".env"),
        extra="ignore",
    )

    openai_api_key: str = Field(default_factory=lambda: "env-placeholder")

    chat_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"

    database_url: str = Field(default_factory=lambda: "env-placeholder")

    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_in_memory: bool = False
    qdrant_collection: str = "kb_chunks"

    rag_chunk_size: int = 512
    rag_chunk_overlap: int = 50
    rag_top_k: int = 3

    support_agent_max_history: int = 10
    triage_batch_size: int = 5

    kb_docs_path: str = "./kb"
    app_env: str = "development"
    log_level: str = "INFO"

@lru_cache
def get_settings() -> Settings:
    return Settings()