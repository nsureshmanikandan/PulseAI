"""LLM factory — returns a configured LLM instance based on LLM_PROVIDER env var.

Uses Settings() directly (not get_settings()) so tests can inject env vars without
fighting the lru_cache.

Accenture GenAI Gateway flow:
  1. Acquire OAuth2 bearer token via client credentials
  2. Call the gateway endpoint with Authorization + X-Authcode + X-User headers
"""

import time
import threading
from typing import Any, Optional
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
    # Accenture gateway detected when token_url is set
    if settings.azure_openai_token_url:
        return AccentureGenAILLM(settings)

    # Standard direct Azure OpenAI
    try:
        from pandasai.llm import AzureOpenAI  # type: ignore[import]
        return AzureOpenAI(
            api_token=settings.azure_openai_api_key or "placeholder",
            azure_endpoint=settings.azure_openai_endpoint or "https://placeholder.openai.azure.com/",
            api_version="2024-02-01",
            deployment_name=settings.azure_openai_deployment or "gpt-4o",
        )
    except ImportError:
        return _AzureOpenAIStub(settings)


def _make_openai(settings: Settings):
    try:
        from pandasai.llm import OpenAI  # type: ignore[import]
        return OpenAI(api_token=settings.openai_api_key or "placeholder")
    except ImportError:
        return _OpenAIStub(settings)


def _make_claude(settings: Settings):
    try:
        from pandasai.llm import BambooLLM  # type: ignore[import]
        return BambooLLM()
    except ImportError:
        return _ClaudeStub(settings)


class AccentureGenAILLM:
    """
    LLM wrapper for the Accenture GenAI Gateway.

    Auth flow: OAuth2 client credentials → bearer token (cached with 5-min buffer).
    Every chat call adds X-Authcode and X-User headers required by the gateway.
    """

    def __init__(self, settings: Settings):
        self._settings = settings
        self._token: Optional[str] = None
        self._token_expiry: float = 0.0
        self._lock = threading.Lock()

    # ------------------------------------------------------------------ #
    # Token management                                                     #
    # ------------------------------------------------------------------ #

    def _get_token(self) -> str:
        with self._lock:
            if self._token and time.time() < self._token_expiry:
                return self._token

            import requests
            s = self._settings
            resp = requests.post(
                s.azure_openai_token_url,
                data={
                    "grant_type": "client_credentials",
                    "client_id": s.azure_openai_token_client_id,
                    "client_secret": s.azure_openai_token_client_secret,
                    "scope": s.azure_openai_token_scope,
                },
                timeout=15,
            )
            resp.raise_for_status()
            payload = resp.json()
            self._token = payload["access_token"]
            expires_in = payload.get("expires_in", 3600)
            self._token_expiry = time.time() + expires_in - 300  # 5-min buffer
            return self._token

    # ------------------------------------------------------------------ #
    # Chat completions                                                     #
    # ------------------------------------------------------------------ #

    def call(self, instruction: Any, context: Any = None) -> str:
        """Called by PandasAI with a prompt string or message list."""
        prompt = self._extract_prompt(instruction)
        return self._chat(prompt)

    def chat(self, prompt: str) -> str:
        """Direct chat — used by narrative.py."""
        return self._chat(prompt)

    def _chat(self, prompt: str) -> str:
        import requests
        s = self._settings
        token = self._get_token()

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Authcode": s.azure_openai_x_authcode,
            "X-User": s.azure_openai_x_user,
        }

        body = {
            "engineId": s.azure_openai_engine_id,
            "modelId": s.azure_openai_model_id,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
        }

        resp = requests.post(
            s.azure_openai_endpoint,
            headers=headers,
            json=body,
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()

        # Standard OpenAI-compatible response shape
        return data["choices"][0]["message"]["content"]

    def chat_stream(self, prompt: str):
        """Generator that yields text chunks via SSE streaming."""
        import requests
        import json as _json
        s = self._settings
        token = self._get_token()

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Authcode": s.azure_openai_x_authcode,
            "X-User": s.azure_openai_x_user,
        }

        body = {
            "engineId": s.azure_openai_engine_id,
            "modelId": s.azure_openai_model_id,
            "messages": [{"role": "user", "content": prompt}],
            "stream": True,
        }

        with requests.post(
            s.azure_openai_endpoint,
            headers=headers,
            json=body,
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
    def _extract_prompt(instruction: Any) -> str:
        """Normalise PandasAI's instruction format to a plain string."""
        if isinstance(instruction, str):
            return instruction
        if isinstance(instruction, list):
            # List of {"role": ..., "content": ...}
            parts = [m.get("content", "") for m in instruction if isinstance(m, dict)]
            return "\n".join(parts)
        # PandasAI AbstractInstruction object
        if hasattr(instruction, "to_string"):
            return instruction.to_string()
        return str(instruction)


# ------------------------------------------------------------------ #
# Stubs (fallback when pandasai not installed)                         #
# ------------------------------------------------------------------ #

class _AzureOpenAIStub:
    def __init__(self, settings: Settings):
        self._settings = settings

    def call(self, instruction, context=None):  # pragma: no cover
        raise NotImplementedError("pandasai is not installed.")


class _OpenAIStub:
    def __init__(self, settings: Settings):
        self._settings = settings

    def call(self, instruction, context=None):  # pragma: no cover
        raise NotImplementedError("pandasai is not installed.")


class _ClaudeStub:
    def __init__(self, settings: Settings):
        self._settings = settings

    def call(self, instruction, context=None):  # pragma: no cover
        raise NotImplementedError("pandasai is not installed.")
