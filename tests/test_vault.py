import pytest
from pathlib import Path
from comb.vault.backends.dotenv import DotEnvBackend


@pytest.fixture
def backend(tmp_path: Path) -> DotEnvBackend:
    """Fresh backend pointing at a temp file for each test."""
    return DotEnvBackend(env_file=tmp_path / ".vault.env")


# ------------------------------------------------------------------ #
# Basic operations
# ------------------------------------------------------------------ #

def test_set_and_get(backend):
    backend.set("openai", "sk-test-123")
    assert backend.get("openai") == "sk-test-123"


def test_get_missing_returns_none(backend):
    assert backend.get("openai") is None


def test_overwrite(backend):
    backend.set("openai", "sk-old")
    backend.set("openai", "sk-new")
    assert backend.get("openai") == "sk-new"


def test_delete_existing(backend):
    backend.set("anthropic", "sk-ant-123")
    result = backend.delete("anthropic")
    assert result is True
    assert backend.get("anthropic") is None


def test_delete_missing_returns_false(backend):
    result = backend.delete("openai")
    assert result is False


# ------------------------------------------------------------------ #
# List
# ------------------------------------------------------------------ #

def test_list_empty(backend):
    assert backend.list() == []


def test_list_multiple(backend):
    backend.set("openai", "sk-1")
    backend.set("anthropic", "sk-2")
    backend.set("gemini", "sk-3")
    assert sorted(backend.list()) == ["anthropic", "gemini", "openai"]


def test_list_does_not_expose_values(backend):
    backend.set("openai", "sk-super-secret")
    listed = backend.list()
    assert "sk-super-secret" not in listed
    assert "openai" in listed


# ------------------------------------------------------------------ #
# Security
# ------------------------------------------------------------------ #

def test_file_permissions(backend):
    """Vault file must be owner read/write only."""
    backend.set("openai", "sk-1")
    mode = oct(backend.env_file.stat().st_mode)[-3:]
    assert mode == "600"


def test_keys_namespaced_in_file(backend):
    """Keys must be stored with COMB_KEY_ prefix."""
    backend.set("openai", "sk-1")
    contents = backend.env_file.read_text()
    assert "COMB_KEY_OPENAI=sk-1" in contents


# ------------------------------------------------------------------ #
# Constants
# ------------------------------------------------------------------ #

def test_supported_providers():
    from comb.constants import SUPPORTED_PROVIDERS
    assert "openai" in SUPPORTED_PROVIDERS
    assert "anthropic" in SUPPORTED_PROVIDERS
    assert "gemini" in SUPPORTED_PROVIDERS