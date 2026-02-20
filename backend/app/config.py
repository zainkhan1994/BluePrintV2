from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Blueprint Memory API"
    database_url: str = "sqlite:///./blueprint_memory.db"
    chroma_path: str = "./data/chroma"
    chroma_collection: str = "blueprint_items"
    embedding_model_version: str = "local-hash-v1"
    embedding_dim: int = 384
    embedding_provider: str = "local_hash"
    embedding_api_url: str | None = None
    embedding_api_key: str | None = None
    embedding_api_model: str = "text-embedding-3-small"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
