import pytest
from comb.agents.queen import AgentSpec, AgentPlan
from comb.agents.runner import run, AgentResult


FAKE_PLAN = AgentPlan(
    goal="build a web scraper",
    agents=[
        AgentSpec(role="researcher", model="gpt-4o-mini", provider="openai"),
        AgentSpec(role="coder", model="claude-haiku-4-5-20251001", provider="anthropic"),
    ],
)


@pytest.fixture(autouse=True)
def mock_complete(monkeypatch):
    monkeypatch.setattr(
        "comb.agents.runner.complete",
        lambda prompt, model, provider: "agent output",
    )


# ------------------------------------------------------------------ #
# Happy path
# ------------------------------------------------------------------ #

def test_run_returns_one_result_per_agent():
    results = run(FAKE_PLAN)
    assert len(results) == len(FAKE_PLAN.agents)


def test_run_result_has_output():
    results = run(FAKE_PLAN)
    for r in results:
        assert r.output == "agent output"
        assert r.error is None


def test_run_returns_agent_result_instances():
    results = run(FAKE_PLAN)
    for r in results:
        assert isinstance(r, AgentResult)


def test_run_passes_role_in_prompt(monkeypatch):
    prompts = []

    def capture(prompt, model, provider):
        prompts.append(prompt)
        return "ok"

    monkeypatch.setattr("comb.agents.runner.complete", capture)
    run(FAKE_PLAN)

    roles = {spec.role for spec in FAKE_PLAN.agents}
    for prompt in prompts:
        assert any(role in prompt for role in roles)


# ------------------------------------------------------------------ #
# Error handling
# ------------------------------------------------------------------ #

def test_run_agent_failure_captured_in_result(monkeypatch):
    monkeypatch.setattr(
        "comb.agents.runner.complete",
        lambda prompt, model, provider: (_ for _ in ()).throw(RuntimeError("API error")),
    )
    results = run(FAKE_PLAN)
    for r in results:
        assert r.error == "API error"
        assert r.output is None


def test_run_all_agents_execute_despite_one_failure(monkeypatch):
    call_count = [0]

    def flaky(prompt, model, provider):
        call_count[0] += 1
        if "researcher" in prompt:
            raise RuntimeError("boom")
        return "ok"

    monkeypatch.setattr("comb.agents.runner.complete", flaky)
    results = run(FAKE_PLAN)

    assert len(results) == 2
    assert call_count[0] == 2
    by_role = {r.role: r for r in results}
    assert by_role["researcher"].error == "boom"
    assert by_role["coder"].output == "ok"
