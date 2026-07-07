from backend.config import Settings


class _LLMStub:
    """Stub LLM for when real providers are not configured."""
    def __init__(self, provider: str):
        self.provider = provider

    def call(self, messages):
        return f"[{self.provider} response placeholder]"


def create_llm():
    settings = Settings()
    provider = settings.llm_provider.lower()
    if provider not in ("azure_openai", "openai", "claude"):
        raise ValueError(
            f"Unsupported LLM provider: {provider}. Choose from: azure_openai, openai, claude"
        )
    return _LLMStub(provider)
