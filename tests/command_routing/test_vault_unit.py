from pathlib import Path

import pytest

from grid.command_routing import vault as vault_module
from grid.command_routing.config import Config
from grid.command_routing.vault import UnknownVaultError, resolve_vault_path


class TestExplicitPath:
    def test_absolute_path(self, tmp_path):
        result = resolve_vault_path(str(tmp_path), config=Config())
        assert result == tmp_path.resolve()

    def test_relative_dot_slash_resolves_against_cwd(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = resolve_vault_path("./work", config=Config())
        assert result == (tmp_path / "work").resolve()

    def test_path_with_dot_bypasses_name_lookup(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        config = Config(default="work", vaults={"work": Path("/elsewhere")})
        result = resolve_vault_path("./work", config=config)
        assert result == (tmp_path / "work").resolve()
        assert result != Path("/elsewhere")

    def test_backslash_bypasses_name_lookup(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        config = Config(default="work", vaults={"work": Path("/elsewhere")})
        result = resolve_vault_path(r"dir\work", config=config)
        assert result == (tmp_path / r"dir\work").resolve()

    def test_expanduser_on_tilde_path(self, tmp_path, monkeypatch):
        monkeypatch.setenv("HOME", str(tmp_path))
        result = resolve_vault_path("~/myvault", config=Config())
        assert result == (tmp_path / "myvault").resolve()


class TestExplicitName:
    def test_registered_name_resolves_to_vault_path(self, tmp_path):
        vault = tmp_path / "work_vault"
        config = Config(default="work", vaults={"work": vault})
        result = resolve_vault_path("work", config=config)
        assert result == vault.resolve()

    def test_unknown_bare_name_raises(self):
        config = Config(default="work", vaults={"work": Path("/x")})
        with pytest.raises(UnknownVaultError) as exc_info:
            resolve_vault_path("typo", config=config)
        assert "typo" in str(exc_info.value)
        assert exc_info.value.name == "typo"

    def test_unknown_bare_name_with_empty_config_raises(self):
        with pytest.raises(UnknownVaultError):
            resolve_vault_path("foo", config=Config())

    def test_error_message_suggests_dot_slash(self):
        with pytest.raises(UnknownVaultError) as exc_info:
            resolve_vault_path("foo", config=Config())
        assert "./foo" in str(exc_info.value)


class TestEnvVar:
    def test_env_var_when_no_explicit(self, tmp_path, monkeypatch):
        monkeypatch.setenv("GRID_VAULT", str(tmp_path))
        result = resolve_vault_path(None, config=Config())
        assert result == tmp_path.resolve()

    def test_explicit_overrides_env(self, tmp_path, monkeypatch):
        other = tmp_path / "other"
        monkeypatch.setenv("GRID_VAULT", str(other))
        result = resolve_vault_path(str(tmp_path), config=Config())
        assert result == tmp_path.resolve()
        assert result != other.resolve()

    def test_env_var_is_path_not_name(self, tmp_path, monkeypatch):
        vault = tmp_path / "work_vault"
        config = Config(default="work", vaults={"work": vault})
        monkeypatch.setenv("GRID_VAULT", "work")
        result = resolve_vault_path(None, config=config)
        assert result == (Path.cwd() / "work").resolve()
        assert result != vault.resolve()


class TestConfigDefault:
    def test_default_used_when_no_explicit_or_env(self, tmp_path, monkeypatch):
        monkeypatch.delenv("GRID_VAULT", raising=False)
        vault = tmp_path / "default_vault"
        config = Config(default="work", vaults={"work": vault})
        result = resolve_vault_path(None, config=config)
        assert result == vault.resolve()

    def test_env_overrides_config_default(self, tmp_path, monkeypatch):
        env_target = tmp_path / "env_target"
        vault = tmp_path / "default_vault"
        config = Config(default="work", vaults={"work": vault})
        monkeypatch.setenv("GRID_VAULT", str(env_target))
        result = resolve_vault_path(None, config=config)
        assert result == env_target.resolve()


class TestPlatformDefault:
    def test_platform_default_when_nothing_set(self, tmp_path, monkeypatch):
        monkeypatch.delenv("GRID_VAULT", raising=False)
        monkeypatch.setattr(vault_module, "user_data_path", lambda *_a, **_k: tmp_path)
        result = resolve_vault_path(None, config=Config())
        assert result == (tmp_path / "vault").resolve()

    def test_config_default_overrides_platform(self, tmp_path, monkeypatch):
        monkeypatch.delenv("GRID_VAULT", raising=False)
        monkeypatch.setattr(vault_module, "user_data_path", lambda *_a, **_k: tmp_path)
        configured = tmp_path / "configured"
        config = Config(default="work", vaults={"work": configured})
        result = resolve_vault_path(None, config=config)
        assert result == configured.resolve()
