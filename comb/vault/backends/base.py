from abc import ABC, abstractmethod


class VaultBackend(ABC):
    """
    Contract every vault backend must follow.

    To add a new backend:
      1. Create a new file in vault/backends/
      2. Subclass VaultBackend
      3. Implement all four methods
      4. Register it in vault/backends/__init__.py
    """

    @abstractmethod
    def set(self, provider: str, api_key: str) -> None:
        """Store or overwrite a credential."""
        ...

    @abstractmethod
    def get(self, provider: str) -> str | None:
        """Retrieve a credential. Returns None if not found."""
        ...

    @abstractmethod
    def delete(self, provider: str) -> bool:
        """Delete a credential. Returns True if it existed."""
        ...

    @abstractmethod
    def list(self) -> list[str]:
        """Return stored provider names. Never return values."""
        ...