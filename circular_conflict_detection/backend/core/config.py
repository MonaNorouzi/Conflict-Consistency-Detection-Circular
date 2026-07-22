from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "circular-conflict-detection"
    vector_db_url: str = "http://qdrant:6333"
    llm_provider: str = "ollama"

    class Config:
        env_file = ".env"


settings = Settings()
