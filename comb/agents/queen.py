import json
import logging
logging.getLogger("LiteLLM").setLevel(logging.ERROR)
from litellm import completion
from pydantic import BaseModel, field_validator

from comb.config import settings
from comb.constants import SUPPORTED_PROVIDERS
from comb.vault import vault


class AgentSpec(BaseModel):
    role: str
    model: str
    provider: str

    @field_validator("provider")
    @classmethod
    def provider_must_be_supported(cls, v: str) -> str:
        if v not in SUPPORTED_PROVIDERS:
            raise ValueError(
                f"Queen returned unsupported provider '{v}'. "
                f"Supported: {', '.join(SUPPORTED_PROVIDERS)}"
            )
        return v


class AgentPlan(BaseModel):
    goal: str
    agents: list[AgentSpec]


_SYSTEM_PROMPT = """\
You are the queen agent of COMB (Collaborative Orchestration of Multi-agent Behavior).
Your job: analyze the user's goal and return a JSON plan of specialized sub-agents to accomplish it.

Rules:
- Use 2-5 agents. More is not always better.
- Only assign providers from the AVAILABLE PROVIDERS list below.
- Use smaller models (e.g. gpt-4o-mini, claude-haiku-4-5) for simple tasks; larger ones for complex reasoning.
- Each agent should have a distinct, focused role.

Respond ONLY with a valid JSON object in this exact shape:
{
  "goal": "<the user's original goal>",
  "agents": [
    {
      "role": "<descriptive role name>",
      "model": "<model id>",
      "provider": "<provider name>"
    }
  ]
}
"""


def plan(goal: str) -> AgentPlan:
    """Ask the queen to decompose a goal into a structured agent plan."""
    api_key = vault.get(settings.queen_provider)
    if settings.queen_provider != "ollama" and api_key is None:
        raise RuntimeError(
            f"No API key stored for queen provider '{settings.queen_provider}'. "
            f"Run: comb add key {settings.queen_provider} <your-api-key>"
        )

    available = vault.list() or SUPPORTED_PROVIDERS
    system = _SYSTEM_PROMPT + f"\nAVAILABLE PROVIDERS: {', '.join(available)}\n"

    response = completion(
        model=f"{settings.queen_provider}/{settings.queen_model}",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": goal},
        ],
        api_key=api_key,
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content
    data = json.loads(raw)
    return AgentPlan(**data)
