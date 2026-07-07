"""LLM factory — returns a configured LLM instance based on LLM_PROVIDER env var.

Uses Settings() directly (not get_settings()) so tests can inject env vars without
fighting the lru_cache.
"""

from backend.config import Settings


def create_llm():
    """Create and return an LLM instance based on the configured LLM_PROVIDER."""
    settings = Settings()  # NOT get_settings() — allows env var injection in tests
    provider = settings.llm_provider.lower()

    if provider == "azure_openai":
        return _make_azure_openai(settings)
    elif provider == "openai":
        return _make_openai(settings)
    elif provider == "claude":
        return _make_claude(settings)
    else:
        raise ValueError(
            f"Unsupported LLM provider: {provider}. "
            "Choose from: azure_openai, openai, claude"
        )


def _make_azure_openai(settings: Settings):
    try:
        from pandasai.llm import AzureOpenAI  # type: ignore[import]
        return AzureOpenAI(
            api_token=settings.azure_openai_api_key or "placeholder",
            azure_endpoint=settings.azure_openai_endpoint or "https://placeholder.openai.azure.com/",
            api_version="2024-02-01",
            deployment_name=settings.azure_openai_deployment or "gpt-4o",
        )
    except ImportError:
        return _AzureOpenAIStub(
            api_token=settings.azure_openai_api_key or "placeholder",
            azure_endpoint=settings.azure_openai_endpoint or "https://placeholder.openai.azure.com/",
        )


def _make_openai(settings: Settings):
    try:
        from pandasai.llm import OpenAI  # type: ignore[import]
        return OpenAI(api_token=settings.openai_api_key or "placeholder")
    except ImportError:
        return _OpenAIStub(api_token=settings.openai_api_key or "placeholder")


def _make_claude(settings: Settings):
    try:
        from pandasai.llm import BambooLLM  # type: ignore[import]
        return BambooLLM()
    except ImportError:
        return _ClaudeStub(api_key=settings.anthropic_api_key or "placeholder")


class _AzureOpenAIStub:
    """Stub AzureOpenAI LLM — used when pandasai is not installed."""

    def __init__(self, api_token: str, azure_endpoint: str, **kwargs):
        self.api_token = api_token
        self.azure_endpoint = azure_endpoint

    def call(self, instruction, context=None):  # pragma: no cover
        raise NotImplementedError("pandasai is not installed.")


class _OpenAIStub:
    """Stub OpenAI LLM — used when pandasai is not installed."""

    def __init__(self, api_token: str):
        self.api_token = api_token

    def call(self, instruction, context=None):  # pragma: no cover
        raise NotImplementedError("pandasai is not installed.")


class _ClaudeStub:
    """Stub Claude LLM — used when pandasai is not installed."""

    def __init__(self, api_key: str):
        self.api_key = api_key

    def call(self, instruction, context=None):  # pragma: no cover
        raise NotImplementedError("pandasai is not installed.")
