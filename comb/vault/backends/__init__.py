from comb.vault.backends.base import VaultBackend
from comb.vault.backends.dotenv import DotEnvBackend

# Registry — add new backends here as a single line
# "keyring":   KeyringBackend,
# "infisical": InfisicalBackend,
# "hashicorp": HashiCorpBackend,
BACKENDS: dict[str, type[VaultBackend]] = {
    "dotenv": DotEnvBackend,
}

__all__ = ["VaultBackend", "DotEnvBackend", "BACKENDS"]