from comb.config import settings
from comb.vault.backends import BACKENDS
from comb.vault.backends.base import VaultBackend


def _load_backend() -> VaultBackend:
    """
    Instantiate the configured backend.
    Raises a clear error if the backend name isn't registered.
    """
    backend_name = settings.vault_backend
    backend_cls = BACKENDS.get(backend_name)

    if backend_cls is None:
        available = ", ".join(BACKENDS.keys())
        raise ValueError(
            f"Unknown vault backend: '{backend_name}'.\n"
            f"Available: {available}\n"
            f"Set COMB_VAULT_BACKEND in your environment."
        )

    if backend_name == "dotenv":
        return backend_cls(env_file=settings.vault_env_file)

    return backend_cls()


# Single shared instance
# Everything in COMB imports this one object
vault: VaultBackend = _load_backend()