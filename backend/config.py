from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    llm_provider: str = "azure_openai"
    azure_openai_api_key: str = ""
    azure_openai_endpoint: str = ""
    azure_openai_deployment: str = "gpt-4o"
    openai_api_key: str = ""
    anthropic_api_key: str = ""

    storage_backend: str = "local"
    azure_storage_connection_string: str = ""
    aws_s3_bucket: str = ""
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    local_storage_path: str = "./uploads"

    database_url: str = "postgresql://pulseai:pulseai@postgres:5432/pulseai"
    redis_url: str = "redis://redis:6379/0"

    max_upload_size_mb: int = 50
    celery_task_timeout: int = 60
    cors_origins: str = "http://localhost:5173"

    class Config:
        env_file = ".env"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]


@lru_cache
def get_settings() -> Settings:
    return Settings()
