import json
import pytest
from unittest.mock import MagicMock
from pydantic import ValidationError

from comb.agents.queen import plan, AgentPlan, AgentSpec


FAKE_PLAN = {
    "goal": "build a web scraper",
    "agents": [
        {"role": "researcher", "model": "gpt-4o-mini", "provider": "openai"},
        {"role": "coder", "model": "claude-haiku-4-5-20251001", "provider": "anthropic"},
    ],
}


@pytest.fixture(autouse=True)
def mock_litellm(monkeypatch):
    mock_response = MagicMock()
    mock_response.choices[0].message.content = json.dumps(FAKE_PLAN)
    monkeypatch.setattr("comb.agents.queen.completion", lambda **kw: mock_response)
    return mock_response


@pytest.fixture(autouse=True)
def mock_vault(monkeypatch):
    monkeypatch.setattr("comb.agents.queen.vault.get", lambda p: "sk-fake")
    monkeypatch.setattr("comb.agents.queen.vault.list", lambda: ["openai", "anthropic"])


# ------------------------------------------------------------------ #
# Happy path
# ------------------------------------------------------------------ #

def test_plan_returns_agent_plan():
    result = plan("build a web scraper")
    assert isinstance(result, AgentPlan)
    assert result.goal == "build a web scraper"


def test_plan_agents_have_correct_fields():
    result = plan("build a web scraper")
    assert len(result.agents) == 2
    for agent in result.agents:
        assert isinstance(agent, AgentSpec)
        assert agent.role
        assert agent.model
        assert agent.provider


# ------------------------------------------------------------------ #
# litellm call verification
# ------------------------------------------------------------------ #

def test_plan_calls_litellm_with_json_mode(monkeypatch):
    calls = []

    def capture(**kw):
        calls.append(kw)
        mock = MagicMock()
        mock.choices[0].message.content = json.dumps(FAKE_PLAN)
        return mock

    monkeypatch.setattr("comb.agents.queen.completion", capture)
    plan("build a web scraper")
    assert calls[0]["response_format"] == {"type": "json_object"}


def test_plan_uses_configured_model_and_provider(monkeypatch):
    calls = []

    def capture(**kw):
        calls.append(kw)
        mock = MagicMock()
        mock.choices[0].message.content = json.dumps(FAKE_PLAN)
        return mock

    monkeypatch.setattr("comb.agents.queen.completion", capture)
    plan("build a web scraper")
    assert calls[0]["model"].startswith("anthropic/")


# ------------------------------------------------------------------ #
# Error handling
# ------------------------------------------------------------------ #

def test_plan_missing_queen_key_raises(monkeypatch):
    monkeypatch.setattr("comb.agents.queen.vault.get", lambda p: None)
    with pytest.raises(RuntimeError, match="comb add key"):
        plan("build a web scraper")


def test_plan_invalid_provider_in_response_raises(monkeypatch):
    bad_plan = {
        "goal": "build a web scraper",
        "agents": [{"role": "coder", "model": "gpt-4o", "provider": "fakeprovider"}],
    }
    mock_response = MagicMock()
    mock_response.choices[0].message.content = json.dumps(bad_plan)
    monkeypatch.setattr("comb.agents.queen.completion", lambda **kw: mock_response)

    with pytest.raises(ValidationError):
        plan("build a web scraper")
