from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field


# ~/.comb/ is the home directory for all comb data
COMB_DIR = Path.home() / ".comb"
COMB_DIR.mkdir(exist_ok=True)


class Settings(BaseSettings):
    """
    Global settings for COMB.
    Any value can be overridden by environment variable.

    Example:
        COMB_VAULT_BACKEND=keyring comb add key openai sk-1234
    """

    # Which vault backend to use.
    # Current:  "dotenv"
    # Future:   "keyring", "infisical", "hashicorp"
    vault_backend: str = Field(
        default="dotenv",
        alias="COMB_VAULT_BACKEND"
    )

    # Where the .env vault file lives (dotenv backend only)
    vault_env_file: Path = Field(
        default=COMB_DIR / ".vault.env",
        alias="COMB_VAULT_ENV_FILE"
    )

    # Queen agent model configuration
    queen_provider: str = Field(
        default="anthropic",
        alias="COMB_QUEEN_PROVIDER"
    )
    queen_model: str = Field(
        default="claude-opus-4-7",
        alias="COMB_QUEEN_MODEL"
    )

    model_config = {"populate_by_name": True}


# Single global instance — import this everywhere
settings = Settings()