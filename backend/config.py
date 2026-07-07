from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    llm_provider: str = "azure_openai"

    # Standard Azure OpenAI (direct)
    azure_openai_api_key: str = ""
    azure_openai_endpoint: str = ""
    azure_openai_deployment: str = "gpt-4o"

    # Accenture GenAI Gateway — OAuth2 client credentials
    azure_openai_tenant_id: str = ""
    azure_openai_token_url: str = ""
    azure_openai_token_client_id: str = ""
    azure_openai_token_client_secret: str = ""
    azure_openai_token_scope: str = ""
    azure_openai_engine_id: str = ""
    azure_openai_model_id: str = ""
    azure_openai_x_authcode: str = ""
    azure_openai_x_user: str = "1"

    openai_api_key: str = ""
    anthropic_api_key: str = ""

    storage_backend: str = "local"
    azure_storage_connection_string: str = ""
    aws_s3_bucket: str = ""
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    local_storage_path: str = "./uploads"

    database_url: str = ""
    redis_url: str = ""

    max_upload_size_mb: int = 50
    celery_task_timeout: int = 60
    cors_origins: str = "http://localhost:5173"

    class Config:
        env_file = ".env"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
