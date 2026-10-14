from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized, typed configuration loaded from environment variables/.env."""
    app_name: str = "CampusMate AI Student Operations API"
    database_url: str = "sqlite:///./students.db"
    ollama_enabled: bool = False
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    n8n_webhook_url: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
