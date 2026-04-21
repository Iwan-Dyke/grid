import tomllib
from pathlib import Path

import typer

from grid.command_routing.config import (
    Config,
    config_file,
    load_config,
    register_vault,
    save_config,
    validate_name,
)
from grid.command_routing.directory import DirState, classify_directory_state
from grid.command_routing.vault import UnknownVaultError, resolve_vault_path
from grid.command_routing.wizard import is_interactive, run_init_wizard

app = typer.Typer()


@app.callback()
def _main() -> None:
    pass


@app.command()
def init(
    vault: str | None = typer.Option(None, "--vault"),
    name: str | None = typer.Option(None, "--name"),
    default: bool = typer.Option(False, "--default"),
    force: bool = typer.Option(False, "--force"),
) -> None:
    config = _load_config_or_exit()

    if vault is None and is_interactive():
        try:
            answers = run_init_wizard(config, name, default, force)
        except (KeyboardInterrupt, EOFError) as e:
            typer.echo("Aborted.", err=True)
            raise typer.Exit(code=1) from e
        vault = answers.vault
        name = answers.name
        default = answers.make_default
        force = answers.force

    try:
        path = resolve_vault_path(vault, config=config)
    except UnknownVaultError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(code=1) from e
    dir_message = _apply_directory_state(path, force=force)

    final_name = name if name is not None else path.name
    try:
        validate_name(final_name)
    except ValueError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(code=1) from e

    try:
        result = register_vault(config, final_name, path, make_default=default)
    except ValueError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(code=1) from e

    if result.config != config:
        save_config(result.config)

    typer.echo(dir_message)
    if result.newly_registered:
        typer.echo(f"Registered vault '{result.name}' at {path}.")
    else:
        typer.echo(f"Vault at {path} is already registered as '{result.name}'.")


def _load_config_or_exit() -> Config:
    try:
        return load_config()
    except tomllib.TOMLDecodeError as e:
        typer.echo(f"Failed to read config at {config_file()}: {e}", err=True)
        raise typer.Exit(code=1) from e


def _apply_directory_state(path: Path, *, force: bool) -> str:
    state = classify_directory_state(path)

    if state is DirState.NOT_A_DIRECTORY:
        typer.echo(f"Path at {path} exists but is not a directory.", err=True)
        raise typer.Exit(code=1)

    if state is DirState.ABSENT:
        try:
            path.mkdir(parents=True, exist_ok=False)
        except OSError as e:
            typer.echo(f"Failed to create vault at {path}: {e}", err=True)
            raise typer.Exit(code=1) from e
        return f"Initialised vault at {path}"

    if state is DirState.EMPTY_OR_VAULT:
        return f"Vault already exists at {path}"

    if force:
        return f"Initialised vault at {path} (forced over existing contents)"

    typer.echo(
        f"Directory at {path} is not empty and does not look like a vault. "
        "Pass --force to adopt it anyway.",
        err=True,
    )
    raise typer.Exit(code=1)
