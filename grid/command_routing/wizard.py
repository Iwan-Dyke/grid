import sys
from dataclasses import dataclass
from pathlib import Path

import typer
from platformdirs import user_data_path
from rich.prompt import Confirm, Prompt

from grid.command_routing.config import Config, find_name_by_path, validate_name
from grid.command_routing.directory import DirState, classify_directory_state


def is_interactive() -> bool:
    return sys.stdin.isatty()


@dataclass(frozen=True)
class WizardAnswers:
    vault: str
    name: str
    make_default: bool
    force: bool


def run_init_wizard(
    config: Config,
    name_flag: str | None,
    default_flag: bool,
    force_flag: bool,
) -> WizardAnswers:
    path_str = _prompt_path()
    path = Path(path_str).expanduser().resolve()
    name = _determine_name(config, path, name_flag)
    make_default = _determine_make_default(config, default_flag)
    force = _determine_force(path, force_flag)
    return WizardAnswers(
        vault=str(path), name=name, make_default=make_default, force=force
    )


def _prompt_path() -> str:
    platform_default = user_data_path("grid") / "vault"
    typer.echo("Where should the vault live?")
    typer.echo(f"  [1] Default location ({platform_default})")
    typer.echo("  [2] Custom path")
    choice = Prompt.ask("Choice", choices=["1", "2"], default="1")
    if choice == "2":
        return Prompt.ask("Vault path")
    return str(platform_default)


def _determine_name(config: Config, path: Path, name_flag: str | None) -> str:
    existing = find_name_by_path(config, path)
    if existing is not None:
        return existing
    if name_flag is not None:
        return name_flag
    while True:
        name = Prompt.ask("Name for this vault", default=path.name)
        try:
            validate_name(name)
        except ValueError as e:
            typer.echo(str(e), err=True)
            continue
        if name in config.vaults:
            typer.echo(
                f"Vault named '{name}' already exists at a different path.",
                err=True,
            )
            continue
        return name


def _determine_make_default(config: Config, default_flag: bool) -> bool:
    if default_flag:
        return True
    if config.default is None:
        return True
    return Confirm.ask("Make this the new default vault?", default=False)


def _determine_force(path: Path, force_flag: bool) -> bool:
    if force_flag:
        return True
    state = classify_directory_state(path)
    if state != DirState.HAS_NON_GRID_CONTENT:
        return False
    typer.echo(
        f"Directory at {path} is not empty and does not look like a vault.",
        err=True,
    )
    return Confirm.ask("Adopt anyway?", default=False)
