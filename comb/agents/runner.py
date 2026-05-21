from concurrent.futures import ThreadPoolExecutor, as_completed
from pydantic import BaseModel

from comb.agents.queen import AgentPlan, AgentSpec
from comb.providers.provider import complete


class AgentResult(BaseModel):
    role: str
    model: str
    provider: str
    output: str | None = None
    error: str | None = None


def _run_agent(spec: AgentSpec, goal: str) -> AgentResult:
    prompt = f"You are a {spec.role}. Work on the following goal:\n\n{goal}"
    try:
        output = complete(prompt, spec.model, spec.provider)
        return AgentResult(role=spec.role, model=spec.model, provider=spec.provider, output=output)
    except Exception as e:
        return AgentResult(role=spec.role, model=spec.model, provider=spec.provider, error=str(e))


def run(agent_plan: AgentPlan) -> list[AgentResult]:
    """Execute all agents in the plan in parallel. Always returns one result per agent."""
    with ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(_run_agent, agent, agent_plan.goal): agent
            for agent in agent_plan.agents
        }
        results = []
        for future in as_completed(futures):
            results.append(future.result())
    return results
