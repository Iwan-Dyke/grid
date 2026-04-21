import os
from pathlib import Path

from platformdirs import user_data_path

from grid.errors import GridError
from grid.command_routing.config import Config, load_config

_PATH_INDICATORS = ("/", "\\", ".")


class UnknownVaultError(GridError):
    def __init__(self, name: str) -> None:
        self.name = name
        super().__init__(
            f"No vault named '{name}' is registered. "
            f"Use './{name}' for a relative path or an absolute path."
        )


def resolve_vault_path(explicit: str | None, config: Config | None = None) -> Path:
    if config is None:
        config = load_config()

    if explicit is not None:
        if any(ch in explicit for ch in _PATH_INDICATORS):
            return Path(explicit).expanduser().resolve()
        if explicit in config.vaults:
            return config.vaults[explicit].expanduser().resolve()
        raise UnknownVaultError(explicit)

    env_value = os.environ.get("GRID_VAULT")
    if env_value:
        return Path(env_value).expanduser().resolve()

    if config.default is not None and config.default in config.vaults:
        return config.vaults[config.default].expanduser().resolve()

    return (user_data_path("grid") / "vault").resolve()
