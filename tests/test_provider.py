import pytest
from unittest.mock import MagicMock
from comb.providers.provider import complete


@pytest.fixture(autouse=True)
def mock_litellm(monkeypatch):
    """Patch litellm.completion so tests never hit real APIs."""
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "test response"
    monkeypatch.setattr("comb.providers.provider.completion", lambda **kw: mock_response)
    return mock_response


@pytest.fixture(autouse=True)
def mock_vault(monkeypatch):
    """Patch vault.get to return a fake key by default."""
    monkeypatch.setattr("comb.providers.provider.vault.get", lambda provider: "sk-fake-key")


# ------------------------------------------------------------------ #
# Happy path
# ------------------------------------------------------------------ #

def test_complete_returns_string():
    result = complete("say hi", "gpt-4o-mini", "openai")
    assert isinstance(result, str)
    assert result == "test response"


def test_complete_passes_correct_model_format(monkeypatch):
    calls = []

    def capture(**kw):
        calls.append(kw)
        mock = MagicMock()
        mock.choices[0].message.content = "ok"
        return mock

    monkeypatch.setattr("comb.providers.provider.completion", capture)
    complete("hello", "gpt-4o", "openai")
    assert calls[0]["model"] == "openai/gpt-4o"


def test_complete_fetches_key_from_vault(monkeypatch):
    fetched = []
    monkeypatch.setattr("comb.providers.provider.vault.get", lambda p: fetched.append(p) or "sk-fake")
    complete("hello", "gpt-4o-mini", "openai")
    assert "openai" in fetched


# ------------------------------------------------------------------ #
# Validation
# ------------------------------------------------------------------ #

def test_complete_unknown_provider_raises():
    with pytest.raises(ValueError, match="Unknown provider"):
        complete("hello", "some-model", "fakeprovider")


def test_complete_missing_key_raises(monkeypatch):
    monkeypatch.setattr("comb.providers.provider.vault.get", lambda p: None)
    with pytest.raises(RuntimeError, match="comb add key"):
        complete("hello", "gpt-4o-mini", "openai")


# ------------------------------------------------------------------ #
# Ollama (local — no key required)
# ------------------------------------------------------------------ #

def test_complete_ollama_no_key_required(monkeypatch):
    monkeypatch.setattr("comb.providers.provider.vault.get", lambda p: None)
    result = complete("hello", "llama3", "ollama")
    assert result == "test response"
