import sys
from pathlib import Path

import pytest

from grid.command_routing.config import Config
from grid.command_routing.wizard import (
    WizardAnswers,
    is_interactive,
    run_init_wizard,
)


def _queue_prompts(monkeypatch, prompts, confirms):
    prompt_iter = iter(prompts)
    confirm_iter = iter(confirms)
    monkeypatch.setattr(
        "rich.prompt.Prompt.ask", lambda *a, **kw: next(prompt_iter)
    )
    monkeypatch.setattr(
        "rich.prompt.Confirm.ask", lambda *a, **kw: next(confirm_iter)
    )


class TestIsInteractive:
    def test_delegates_to_stdin_isatty_true(self, monkeypatch):
        monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
        assert is_interactive() is True

    def test_delegates_to_stdin_isatty_false(self, monkeypatch):
        monkeypatch.setattr(sys.stdin, "isatty", lambda: False)
        assert is_interactive() is False


class TestPathPrompt:
    def test_default_location_choice_returns_platform_default(
        self, monkeypatch, tmp_path
    ):
        monkeypatch.setattr(
            "grid.command_routing.wizard.user_data_path",
            lambda *a, **kw: tmp_path,
        )
        _queue_prompts(monkeypatch, prompts=["1", "myname"], confirms=[])
        result = run_init_wizard(Config(), None, False, False)
        expected = (tmp_path / "vault").resolve()
        assert result.vault == str(expected)

    def test_custom_path_choice_returns_typed_path(self, monkeypatch, tmp_path):
        custom = tmp_path / "my_vault"
        _queue_prompts(
            monkeypatch, prompts=["2", str(custom), "myname"], confirms=[]
        )
        result = run_init_wizard(Config(), None, False, False)
        expected = custom.resolve()
        assert result.vault == str(expected)


class TestNamePrompt:
    def test_accepts_valid_name(self, monkeypatch, tmp_path):
        custom = tmp_path / "my_vault"
        _queue_prompts(
            monkeypatch, prompts=["2", str(custom), "my-vault"], confirms=[]
        )
        result = run_init_wizard(Config(), None, False, False)
        assert result.name == "my-vault"

    def test_reprompts_on_invalid_shape(self, monkeypatch, tmp_path, capsys):
        custom = tmp_path / "my_vault"
        _queue_prompts(
            monkeypatch,
            prompts=["2", str(custom), "has space", "good-name"],
            confirms=[],
        )
        result = run_init_wizard(Config(), None, False, False)
        captured = capsys.readouterr()
        assert "Invalid vault name" in captured.err
        assert result.name == "good-name"

    def test_reprompts_on_collision(self, monkeypatch, tmp_path, capsys):
        other = tmp_path / "other"
        config = Config(default="taken", vaults={"taken": other})
        custom = tmp_path / "new_vault"
        _queue_prompts(
            monkeypatch,
            prompts=["2", str(custom), "taken", "fresh"],
            confirms=[False],
        )
        result = run_init_wizard(config, None, False, False)
        captured = capsys.readouterr()
        assert "already exists at a different path" in captured.err
        assert result.name == "fresh"

    def test_skipped_when_name_flag_provided(self, monkeypatch, tmp_path):
        custom = tmp_path / "my_vault"
        _queue_prompts(
            monkeypatch, prompts=["2", str(custom)], confirms=[]
        )
        result = run_init_wizard(Config(), "flagname", False, False)
        assert result.name == "flagname"

    def test_skipped_when_path_already_registered(self, monkeypatch, tmp_path):
        existing = (tmp_path / "existing").resolve()
        config = Config(default="known", vaults={"known": existing})
        _queue_prompts(
            monkeypatch, prompts=["2", str(existing)], confirms=[False]
        )
        result = run_init_wizard(config, "ignored_flag", False, False)
        assert result.name == "known"


class TestMakeDefaultPrompt:
    def test_skipped_when_default_flag_true(self, monkeypatch, tmp_path):
        other = tmp_path / "other"
        config = Config(default="first", vaults={"first": other})
        custom = tmp_path / "new_vault"
        _queue_prompts(
            monkeypatch, prompts=["2", str(custom), "new"], confirms=[]
        )
        result = run_init_wizard(config, None, True, False)
        assert result.make_default is True

    def test_skipped_when_config_default_is_none(self, monkeypatch, tmp_path):
        custom = tmp_path / "first_vault"
        _queue_prompts(
            monkeypatch, prompts=["2", str(custom), "first"], confirms=[]
        )
        result = run_init_wizard(Config(), None, False, False)
        assert result.make_default is True

    def test_asked_when_config_has_default_and_flag_false(
        self, monkeypatch, tmp_path
    ):
        other = tmp_path / "other"
        config = Config(default="first", vaults={"first": other})
        custom = tmp_path / "new_vault"
        _queue_prompts(
            monkeypatch,
            prompts=["2", str(custom), "second"],
            confirms=[True],
        )
        result = run_init_wizard(config, None, False, False)
        assert result.make_default is True

    def test_asked_answer_no_returns_false(self, monkeypatch, tmp_path):
        other = tmp_path / "other"
        config = Config(default="first", vaults={"first": other})
        custom = tmp_path / "new_vault"
        _queue_prompts(
            monkeypatch,
            prompts=["2", str(custom), "second"],
            confirms=[False],
        )
        result = run_init_wizard(config, None, False, False)
        assert result.make_default is False


class TestAdoptPrompt:
    def test_skipped_when_force_flag_true(self, monkeypatch, tmp_path):
        target = tmp_path / "has_content"
        target.mkdir()
        (target / "random.txt").write_text("stray")
        _queue_prompts(
            monkeypatch, prompts=["2", str(target), "adopted"], confirms=[]
        )
        result = run_init_wizard(Config(), None, False, True)
        assert result.force is True

    def test_skipped_when_directory_has_no_non_grid_content(
        self, monkeypatch, tmp_path
    ):
        target = tmp_path / "absent_path"
        _queue_prompts(
            monkeypatch, prompts=["2", str(target), "fresh"], confirms=[]
        )
        result = run_init_wizard(Config(), None, False, False)
        assert result.force is False

    def test_asked_when_non_grid_content_and_force_false(
        self, monkeypatch, tmp_path, capsys
    ):
        target = tmp_path / "has_content"
        target.mkdir()
        (target / "random.txt").write_text("stray")
        _queue_prompts(
            monkeypatch,
            prompts=["2", str(target), "adopted"],
            confirms=[True],
        )
        result = run_init_wizard(Config(), None, False, False)
        captured = capsys.readouterr()
        assert "not empty" in captured.err
        assert result.force is True

    def test_asked_answer_no_returns_false(self, monkeypatch, tmp_path):
        target = tmp_path / "has_content"
        target.mkdir()
        (target / "random.txt").write_text("stray")
        _queue_prompts(
            monkeypatch,
            prompts=["2", str(target), "rejected"],
            confirms=[False],
        )
        result = run_init_wizard(Config(), None, False, False)
        assert result.force is False


class TestKeyboardInterruptBubbles:
    def test_bubbles_keyboard_interrupt_from_prompt(self, monkeypatch):
        def boom(*a, **kw):
            raise KeyboardInterrupt

        monkeypatch.setattr("rich.prompt.Prompt.ask", boom)
        monkeypatch.setattr(
            "rich.prompt.Confirm.ask", lambda *a, **kw: False
        )
        with pytest.raises(KeyboardInterrupt):
            run_init_wizard(Config(), None, False, False)


class TestWizardAnswersFrozen:
    def test_answers_is_frozen_dataclass(self):
        answers = WizardAnswers(
            vault="/tmp/v", name="n", make_default=False, force=False
        )
        with pytest.raises(Exception):
            answers.vault = "other"
