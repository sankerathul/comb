from enum import Enum


class Provider(str, Enum):
    """
    Supported AI providers.
    Add new providers here as COMB grows.
    """
    OPENAI    = "openai"
    ANTHROPIC = "anthropic"
    GEMINI    = "gemini"
    GROQ      = "groq"
    MISTRAL   = "mistral"
    OLLAMA    = "ollama"


# Human readable list for error messages and help text
SUPPORTED_PROVIDERS = [p.value for p in Provider]