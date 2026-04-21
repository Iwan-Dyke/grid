import tomllib
from pathlib import Path

from grid.command_routing import app
from grid.command_routing import vault as vault_module
from grid.command_routing.config import Config, load_config


class TestPlatformDefault:
    def test_platform_default_used_when_no_flag_or_env(
        self, runner, tmp_path, monkeypatch, config_path
    ):
        monkeypatch.setattr(
            vault_module,
            "user_data_path",
            lambda *args, **kwargs: tmp_path,
        )
        result = runner.invoke(app, ["init"])
        expected = (tmp_path / "vault").resolve()
        assert result.exit_code == 0
        assert expected.is_dir()
        assert str(expected) in result.stdout
        assert "Initialised" in result.stdout
        assert config_path.is_file()
        with open(config_path, "rb") as f:
            data = tomllib.load(f)
        default_name = data["default"]
        assert default_name in data["vaults"]
        assert data["vaults"][default_name]["path"] == str(expected)


class TestRelativePathResolution:
    def test_relative_path_becomes_absolute_in_stdout(
        self, runner, tmp_path, monkeypatch
    ):
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["init", "--vault", "./relative_vault"])
        expected = (tmp_path / "relative_vault").resolve()
        assert result.exit_code == 0
        assert expected.is_dir()
        assert str(expected) in result.stdout


class TestMkdirFailure:
    def test_permission_error_exits_1_with_stderr(self, runner, tmp_path, monkeypatch):
        target = tmp_path / "vault"

        def boom(self, *args, **kwargs):
            raise PermissionError("denied")

        monkeypatch.setattr(Path, "mkdir", boom)
        result = runner.invoke(app, ["init", "--vault", str(target)])
        assert result.exit_code == 1
        assert "Failed to create vault" in result.stderr


class TestForceDoesNotOverrideFileError:
    def test_force_still_errors_when_path_is_file(self, runner, tmp_path):
        target = tmp_path / "vault"
        target.write_text("I am a file")
        result = runner.invoke(app, ["init", "--vault", str(target), "--force"])
        assert result.exit_code == 1
        assert "not a directory" in result.stderr


class TestStreamRouting:
    def test_success_message_goes_to_stdout_not_stderr(self, runner, tmp_path):
        target = tmp_path / "vault"
        result = runner.invoke(app, ["init", "--vault", str(target)])
        assert result.exit_code == 0
        assert "Initialised" in result.stdout
        assert "Initialised" not in result.stderr

    def test_error_message_goes_to_stderr_not_stdout(self, runner, tmp_path):
        target = tmp_path / "vault"
        target.mkdir()
        (target / "random.txt").write_text("stray")
        result = runner.invoke(app, ["init", "--vault", str(target)])
        assert result.exit_code == 1
        assert "not empty" in result.stderr
        assert "not empty" not in result.stdout


class TestConfigLoad:
    def test_absent_config_file_is_not_error(self, config_path):
        assert not config_path.exists()
        result = load_config()
        assert result == Config()


class TestAtomicWrite:
    def test_atomic_config_write_no_tmp_leftover(self, runner, tmp_path, config_path):
        target = tmp_path / "vault"
        result = runner.invoke(app, ["init", "--vault", str(target)])
        assert result.exit_code == 0
        leftovers = list(config_path.parent.glob("*.tmp"))
        assert leftovers == []


class TestMalformedConfig:
    def test_malformed_toml_exits_with_stderr_error(
        self, runner, tmp_path, config_path
    ):
        config_path.write_bytes(b"not valid = = toml")
        target = tmp_path / "vault"
        result = runner.invoke(app, ["init", "--vault", str(target)])
        assert result.exit_code != 0
        assert result.stderr


class TestInvalidName:
    def test_invalid_name_rejected_with_space(self, runner, tmp_path):
        target = tmp_path / "vault"
        result = runner.invoke(
            app, ["init", "--vault", str(target), "--name", "has space"]
        )
        assert result.exit_code == 1
        assert "Invalid vault name" in result.stderr

    def test_invalid_name_rejected_with_dot(self, runner, tmp_path):
        target = tmp_path / "vault"
        result = runner.invoke(
            app, ["init", "--vault", str(target), "--name", "my.vault"]
        )
        assert result.exit_code == 1
        assert "Invalid vault name" in result.stderr
