from pathlib import Path
from dotenv import dotenv_values
from comb.vault.backends.base import VaultBackend


class DotEnvBackend(VaultBackend):
    """
    Stores credentials in ~/.comb/.vault.env

    File never sits inside your project — 
    so it can never be accidentally committed to git.

    Format inside the file:
        COMB_KEY_OPENAI=sk-1234...
        COMB_KEY_ANTHROPIC=sk-ant-...
    """

    PREFIX = "COMB_KEY_"

    def __init__(self, env_file: Path):
        self.env_file = env_file
        if not self.env_file.exists():
            self.env_file.touch(mode=0o600)

    def _to_env_key(self, provider: str) -> str:
        """openai → COMB_KEY_OPENAI"""
        return f"{self.PREFIX}{provider.upper()}"

    def _from_env_key(self, env_key: str) -> str:
        """COMB_KEY_OPENAI → openai"""
        return env_key.removeprefix(self.PREFIX).lower()

    def _read_all(self) -> dict[str, str]:
        return dict(dotenv_values(self.env_file))

    def _write_all(self, data: dict[str, str]) -> None:
        lines = [f"{k}={v}" for k, v in data.items()]
        self.env_file.write_text("\n".join(lines) + "\n")
        self.env_file.chmod(0o600)

    def set(self, provider: str, api_key: str) -> None:
        data = self._read_all()
        data[self._to_env_key(provider)] = api_key
        self._write_all(data)

    def get(self, provider: str) -> str | None:
        data = self._read_all()
        return data.get(self._to_env_key(provider))

    def delete(self, provider: str) -> bool:
        data = self._read_all()
        env_key = self._to_env_key(provider)
        if env_key not in data:
            return False
        del data[env_key]
        self._write_all(data)
        return True

    def list(self) -> list[str]:
        data = self._read_all()
        return [
            self._from_env_key(k)
            for k in data
            if k.startswith(self.PREFIX)
        ]