"""LLM factory — returns a configured LLM instance based on LLM_PROVIDER env var.

Accenture lbpass gateway is standard Azure OpenAI-compatible:
  POST {endpoint}/openai/deployments/{deployment}/chat/completions?api-version={version}
  Header: api-key: {AZURE_OPENAI_API_KEY}
  No OAuth2 token acquisition needed.
"""

from backend.config import Settings


def create_llm():
    """Create and return an LLM instance based on the configured LLM_PROVIDER."""
    settings = Settings()
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
    return AccentureLbpassLLM(settings)


def _make_openai(settings: Settings):
    try:
        from pandasai.llm import OpenAI  # type: ignore[import]
        return OpenAI(api_token=settings.openai_api_key or "placeholder")
    except ImportError:
        return _OpenAIStub(settings)


def _make_claude(settings: Settings):
    return _ClaudeStub(settings)


class AccentureLbpassLLM:
    """
    LLM for Accenture GenAI lbpass gateway (Azure OpenAI-compatible).

    Endpoint: {AZURE_OPENAI_ENDPOINT}/openai/deployments/{deployment}/chat/completions
    Auth:     api-key header only — no OAuth2 token needed.
    """

    def __init__(self, settings: Settings):
        self._settings = settings

    def _url(self) -> str:
        s = self._settings
        base = s.azure_openai_endpoint.rstrip("/")
        return f"{base}/openai/deployments/{s.azure_openai_deployment}/chat/completions?api-version={s.azure_openai_api_version}"

    def _headers(self) -> dict:
        return {
            "api-key": self._settings.lbpass_api_key,
            "Content-Type": "application/json",
        }

    def call(self, instruction, context=None) -> str:
        """Called by PandasAI with a prompt string or message list."""
        prompt = self._extract_prompt(instruction)
        return self.chat(prompt)

    def chat(self, prompt: str) -> str:
        """Synchronous chat completion."""
        import requests
        resp = requests.post(
            self._url(),
            headers=self._headers(),
            json={"messages": [{"role": "user", "content": prompt}], "max_tokens": 2000},
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

    def chat_stream(self, prompt: str):
        """SSE streaming — yields text chunks."""
        import requests, json as _json
        with requests.post(
            self._url(),
            headers=self._headers(),
            json={"messages": [{"role": "user", "content": prompt}], "max_tokens": 2000, "stream": True},
            stream=True,
            timeout=60,
        ) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if not line:
                    continue
                text = line.decode("utf-8") if isinstance(line, bytes) else line
                if text.startswith("data: "):
                    text = text[6:]
                if text == "[DONE]":
                    break
                try:
                    chunk = _json.loads(text)
                    delta = chunk["choices"][0]["delta"].get("content", "")
                    if delta:
                        yield delta
                except (_json.JSONDecodeError, KeyError):
                    continue

    @staticmethod
    def _extract_prompt(instruction) -> str:
        if isinstance(instruction, str):
            return instruction
        if isinstance(instruction, list):
            return "\n".join(m.get("content", "") for m in instruction if isinstance(m, dict))
        if hasattr(instruction, "to_string"):
            return instruction.to_string()
        return str(instruction)


class _OpenAIStub:
    def __init__(self, settings: Settings):
        self._settings = settings

    def call(self, instruction, context=None):  # pragma: no cover
        raise NotImplementedError("pandasai not installed.")


class _ClaudeStub:
    def __init__(self, settings: Settings):
        self._settings = settings

    def call(self, instruction, context=None):  # pragma: no cover
        raise NotImplementedError("Claude provider not yet wired.")
