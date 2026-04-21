import os
import re
import tomllib
from dataclasses import dataclass, field, replace
from pathlib import Path

import tomli_w
from platformdirs import user_config_path

NAME_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")


@dataclass(frozen=True)
class Config:
    default: str | None = None
    vaults: dict[str, Path] = field(default_factory=dict)


def config_file() -> Path:
    return user_config_path("grid") / "config.toml"


def load_config() -> Config:
    path = config_file()
    if not path.exists():
        return Config()

    with path.open("rb") as f:
        data = tomllib.load(f)

    default = data.get("default")
    vaults_raw = data.get("vaults", {})
    vaults: dict[str, Path] = {}
    for name, entry in vaults_raw.items():
        vaults[name] = Path(entry["path"])

    return Config(default=default, vaults=vaults)


def save_config(config: Config) -> None:
    path = config_file()
    path.parent.mkdir(parents=True, exist_ok=True)

    document: dict[str, object] = {}
    if config.default is not None:
        document["default"] = config.default
    if config.vaults:
        document["vaults"] = {
            name: {"path": str(vault_path)}
            for name, vault_path in config.vaults.items()
        }

    tmp = path.parent / f"{path.name}.tmp"
    with tmp.open("wb") as f:
        tomli_w.dump(document, f)
    os.replace(tmp, path)


def find_name_by_path(config: Config, path: Path) -> str | None:
    for name, registered_path in config.vaults.items():
        if registered_path == path:
            return name
    return None


def validate_name(name: str) -> None:
    if not name or not NAME_PATTERN.match(name):
        raise ValueError(
            f"Invalid vault name '{name}'. "
            "Use letters, digits, hyphens, or underscores only."
        )


@dataclass(frozen=True)
class RegistrationResult:
    config: Config
    name: str
    newly_registered: bool


def register_vault(
    config: Config, name: str, path: Path, make_default: bool
) -> RegistrationResult:
    existing_name = find_name_by_path(config, path)
    if existing_name is not None:
        if make_default and config.default != existing_name:
            promoted = replace(config, default=existing_name)
            return RegistrationResult(promoted, existing_name, False)
        return RegistrationResult(config, existing_name, False)

    if name in config.vaults:
        raise ValueError(f"Vault named '{name}' already exists at a different path.")

    new_vaults = {**config.vaults, name: path}
    new_default = name if config.default is None or make_default else config.default
    new_config = replace(config, default=new_default, vaults=new_vaults)
    return RegistrationResult(new_config, name, True)
