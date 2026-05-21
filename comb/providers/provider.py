import logging
logging.getLogger("LiteLLM").setLevel(logging.ERROR)
from litellm import completion
from comb.vault import vault
from comb.constants import Provider, SUPPORTED_PROVIDERS


def complete(prompt: str, model: str, provider: str) -> str:
    """Call any supported provider and return the text response."""
    if provider not in SUPPORTED_PROVIDERS:
        raise ValueError(
            f"Unknown provider '{provider}'. "
            f"Supported: {', '.join(SUPPORTED_PROVIDERS)}"
        )

    api_key = vault.get(provider)

    # Ollama runs locally — no API key needed
    if provider != Provider.OLLAMA and api_key is None:
        raise RuntimeError(
            f"No API key stored for '{provider}'. "
            f"Run: comb add key {provider} <your-api-key>"
        )

    response = completion(
        model=f"{provider}/{model}",
        messages=[{"role": "user", "content": prompt}],
        api_key=api_key,
    )

    return response.choices[0].message.content
