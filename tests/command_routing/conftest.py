import pytest
from typer.testing import CliRunner


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture(autouse=True)
def _isolate_env_and_config(monkeypatch, tmp_path):
    monkeypatch.delenv("GRID_VAULT", raising=False)
    config_home = tmp_path / "_grid_config"
    config_home.mkdir()
    monkeypatch.setattr(
        "grid.command_routing.config.user_config_path",
        lambda *args, **kwargs: config_home,
    )


@pytest.fixture
def config_path(tmp_path):
    return tmp_path / "_grid_config" / "config.toml"
