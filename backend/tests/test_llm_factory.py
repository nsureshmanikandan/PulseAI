import os
import pytest
from unittest.mock import patch, MagicMock


def test_azure_openai_provider():
    with patch.dict(os.environ, {
        "LLM_PROVIDER": "azure_openai",
        "AZURE_OPENAI_API_KEY": "test-key",
        "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/",
        "DATABASE_URL": "sqlite:///:memory:",
        "REDIS_URL": "redis://localhost:6379/0",
    }):
        from backend.modules.ai.llm_factory import create_llm
        llm = create_llm()
        assert llm is not None


def test_unsupported_provider_raises():
    with patch.dict(os.environ, {
        "LLM_PROVIDER": "gemini",
        "DATABASE_URL": "sqlite:///:memory:",
        "REDIS_URL": "redis://localhost:6379/0",
    }):
        from backend.modules.ai.llm_factory import create_llm
        with pytest.raises(ValueError, match="Unsupported LLM provider"):
            create_llm()


def test_openai_provider():
    with patch.dict(os.environ, {
        "LLM_PROVIDER": "openai",
        "OPENAI_API_KEY": "test-key",
        "DATABASE_URL": "sqlite:///:memory:",
        "REDIS_URL": "redis://localhost:6379/0",
    }):
        from backend.modules.ai.llm_factory import create_llm
        llm = create_llm()
        assert llm is not None
