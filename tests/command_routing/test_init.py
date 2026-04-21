import tomllib

from pytest_bdd import scenario, given, when, then, parsers

from grid.command_routing import app


@scenario("features/init.feature", "Fresh path is created")
def test_fresh_path_is_created():
    pass


@scenario("features/init.feature", "Empty directory is adopted idempotently")
def test_empty_directory_is_adopted():
    pass


@scenario("features/init.feature", "Existing grid vault is idempotent")
def test_existing_vault_is_idempotent():
    pass


@scenario("features/init.feature", "Non-grid content without --force is rejected")
def test_non_grid_without_force_rejected():
    pass


@scenario("features/init.feature", "Non-grid content with --force is adopted")
def test_non_grid_with_force_adopted():
    pass


@scenario("features/init.feature", "Hidden files do not count as content")
def test_hidden_files_do_not_count():
    pass


@scenario("features/init.feature", "Path pointing at a file errors")
def test_path_at_file_errors():
    pass


@scenario("features/init.feature", "Forcing does not override the file-at-path error")
def test_force_does_not_override_file_error():
    pass


@scenario("features/init.feature", "--vault takes precedence over GRID_VAULT")
def test_vault_flag_beats_env():
    pass


@scenario("features/init.feature", "GRID_VAULT is used when --vault is absent")
def test_env_used_without_flag():
    pass


@scenario("features/init.feature", "Missing parent directories are created")
def test_missing_parents_created():
    pass


@scenario("features/init.feature", "First init writes config with the vault as default")
def test_first_init_writes_config():
    pass


@scenario(
    "features/init.feature",
    "Second init without --default preserves existing default",
)
def test_second_init_preserves_default():
    pass


@scenario("features/init.feature", "Second init with --default switches default")
def test_second_init_switches_default():
    pass


@scenario("features/init.feature", "Re-init on a registered path is idempotent")
def test_reinit_registered_path_idempotent():
    pass


@scenario(
    "features/init.feature",
    "--name is ignored when path is already registered",
)
def test_name_ignored_when_registered():
    pass


@scenario("features/init.feature", "Name collision at different path errors")
def test_name_collision_different_path_errors():
    pass


@scenario(
    "features/init.feature",
    "--vault with a registered name resolves to that vault's path",
)
def test_vault_flag_resolves_registered_name():
    pass


@scenario("features/init.feature", "--vault with leading ./ bypasses name lookup")
def test_dot_slash_bypasses_name_lookup():
    pass


@scenario("features/init.feature", "Wizard: default location chosen")
def test_wizard_default_location():
    pass


@scenario("features/init.feature", "Wizard: custom path chosen")
def test_wizard_custom_path():
    pass


@scenario("features/init.feature", "Wizard accepts valid name")
def test_wizard_accepts_valid_name():
    pass


@scenario("features/init.feature", "Wizard re-prompts on invalid name")
def test_wizard_reprompts_invalid_name():
    pass


@scenario("features/init.feature", "Wizard re-prompts on name collision")
def test_wizard_reprompts_name_collision():
    pass


@scenario(
    "features/init.feature",
    "Wizard make-default answered yes switches default",
)
def test_wizard_make_default_yes():
    pass


@scenario(
    "features/init.feature",
    "Wizard make-default answered no preserves existing default",
)
def test_wizard_make_default_no():
    pass


@scenario("features/init.feature", "Wizard adopt answered yes adopts non-grid content")
def test_wizard_adopt_yes():
    pass


@scenario("features/init.feature", "Wizard adopt answered no rejects with error")
def test_wizard_adopt_no():
    pass


@scenario("features/init.feature", "Wizard does not activate when --vault is passed")
def test_wizard_inactive_with_vault_flag():
    pass


@scenario("features/init.feature", "Wizard does not activate when stdin is not a TTY")
def test_wizard_inactive_without_tty():
    pass


@scenario("features/init.feature", "Wizard skips name prompt when --name is passed")
def test_wizard_skips_name_with_name_flag():
    pass


@scenario(
    "features/init.feature", "Wizard skips default prompt when --default is passed"
)
def test_wizard_skips_default_with_flag():
    pass


@scenario("features/init.feature", "Wizard skips adopt prompt when --force is passed")
def test_wizard_skips_adopt_with_force():
    pass


@given("a vault path that does not exist", target_fixture="vault_path")
def vault_path_absent(tmp_path):
    return tmp_path / "vault"


@given("an empty vault directory", target_fixture="vault_path")
def vault_path_empty(tmp_path):
    path = tmp_path / "vault"
    path.mkdir()
    return path


@given("a vault directory containing a grid-style note", target_fixture="vault_path")
def vault_path_with_grid_note(tmp_path):
    path = tmp_path / "vault"
    path.mkdir()
    (path / "20260409221400-note.md").write_text("---\nid: 20260409221400\n---\nbody\n")
    return path


@given("a vault directory containing a non-grid file", target_fixture="vault_path")
def vault_path_with_non_grid_file(tmp_path):
    path = tmp_path / "vault"
    path.mkdir()
    (path / "random.txt").write_text("stray content")
    return path


@given("a vault directory containing only hidden entries", target_fixture="vault_path")
def vault_path_with_hidden_entries(tmp_path):
    path = tmp_path / "vault"
    path.mkdir()
    (path / ".DS_Store").write_text("metadata")
    (path / ".git").mkdir()
    return path


@given("a path that points at an existing file", target_fixture="vault_path")
def vault_path_is_file(tmp_path):
    path = tmp_path / "vault"
    path.write_text("I am a file, not a directory")
    return path


@given("a vault path with missing parent directories", target_fixture="vault_path")
def vault_path_missing_parents(tmp_path):
    return tmp_path / "missing" / "parents" / "vault"


@given("GRID_VAULT is set to a path that does not exist", target_fixture="env_path")
def set_env_vault(tmp_path, monkeypatch):
    path = tmp_path / "env_vault"
    monkeypatch.setenv("GRID_VAULT", str(path))
    return path


@given("a different vault path that does not exist", target_fixture="vault_path")
def different_vault_path(tmp_path):
    return tmp_path / "flag_vault"


@when("grid init runs with that --vault path", target_fixture="result")
def run_init(runner, vault_path):
    return runner.invoke(app, ["init", "--vault", str(vault_path)])


@when("grid init runs with that --vault path and --force", target_fixture="result")
def run_init_force(runner, vault_path):
    return runner.invoke(app, ["init", "--vault", str(vault_path), "--force"])


@when("grid init runs with the different path via --vault", target_fixture="result")
def run_init_flag_over_env(runner, vault_path):
    return runner.invoke(app, ["init", "--vault", str(vault_path)])


@when("grid init runs with no --vault flag", target_fixture="result")
def run_init_no_flag(runner):
    return runner.invoke(app, ["init"])


@then("the directory exists")
def directory_exists(vault_path):
    assert vault_path.is_dir()


@then("the different path exists")
def different_path_exists(vault_path):
    assert vault_path.is_dir()


@then("the GRID_VAULT path does not exist")
def env_path_absent(env_path):
    assert not env_path.exists()


@then("the GRID_VAULT path exists")
def env_path_exists(env_path):
    assert env_path.is_dir()


@then("the non-grid file still exists")
def non_grid_file_preserved(vault_path):
    assert (vault_path / "random.txt").read_text() == "stray content"


@then(parsers.parse('stdout contains "{text}"'))
def stdout_contains(result, text):
    assert text in result.stdout


@then(parsers.parse('stderr contains "{text}"'))
def stderr_contains(result, text):
    assert text in result.stderr


@then("stdout contains the absolute vault path")
def stdout_contains_path(result, vault_path):
    assert str(vault_path.resolve()) in result.stdout


@then("stderr contains the absolute vault path")
def stderr_contains_path(result, vault_path):
    assert str(vault_path.resolve()) in result.stderr


@then("stdout contains the different absolute path")
def stdout_contains_different_path(result, vault_path):
    assert str(vault_path.resolve()) in result.stdout


@then("stdout contains the GRID_VAULT absolute path")
def stdout_contains_env_path(result, env_path):
    assert str(env_path.resolve()) in result.stdout


@then(parsers.parse("the exit code is {code:d}"))
def check_exit_code(result, code):
    assert result.exit_code == code


@given(
    "a first vault is already registered as default", target_fixture="first_vault_path"
)
def first_vault_registered(runner, tmp_path):
    path = tmp_path / "first_vault"
    result = runner.invoke(app, ["init", "--vault", str(path), "--name", "first"])
    assert result.exit_code == 0
    return path.resolve()


@given("a second vault path that does not exist", target_fixture="second_vault_path")
def second_vault_path_absent(tmp_path):
    return tmp_path / "second_vault"


@given("a vault is registered at a path", target_fixture="registered_vault_path")
def vault_registered_at_path(runner, tmp_path):
    path = tmp_path / "registered_vault"
    result = runner.invoke(app, ["init", "--vault", str(path), "--name", "foo"])
    assert result.exit_code == 0
    return path.resolve()


@given(
    parsers.parse('a vault named "{name}" is registered at a path'),
    target_fixture="named_vault_path",
)
def vault_named_registered(runner, tmp_path, name):
    path = tmp_path / f"{name}_vault"
    result = runner.invoke(app, ["init", "--vault", str(path), "--name", name])
    assert result.exit_code == 0
    return path.resolve()


@given("the working directory is a fresh temp directory", target_fixture="cwd_dir")
def set_cwd(monkeypatch, tmp_path):
    cwd = tmp_path / "cwd_home"
    cwd.mkdir()
    monkeypatch.chdir(cwd)
    return cwd


@when(
    parsers.parse('grid init runs with the second vault path and name "{name}"'),
    target_fixture="result",
)
def run_init_second_vault(runner, second_vault_path, name):
    return runner.invoke(
        app, ["init", "--vault", str(second_vault_path), "--name", name]
    )


@when(
    parsers.parse(
        'grid init runs with the second vault path and name "{name}" and --default'
    ),
    target_fixture="result",
)
def run_init_second_vault_default(runner, second_vault_path, name):
    return runner.invoke(
        app,
        ["init", "--vault", str(second_vault_path), "--name", name, "--default"],
    )


@when("grid init runs with that registered path again", target_fixture="result")
def run_init_reregister(runner, registered_vault_path):
    return runner.invoke(app, ["init", "--vault", str(registered_vault_path)])


@when(
    parsers.parse('grid init runs with that registered path and name "{name}"'),
    target_fixture="result",
)
def run_init_registered_with_name(runner, named_vault_path, name):
    return runner.invoke(
        app, ["init", "--vault", str(named_vault_path), "--name", name]
    )


@when(
    parsers.parse('grid init runs with the different path and name "{name}"'),
    target_fixture="result",
)
def run_init_different_path_with_name(runner, vault_path, name):
    return runner.invoke(app, ["init", "--vault", str(vault_path), "--name", name])


@when(
    parsers.parse('grid init runs with --vault "{vault_arg}"'),
    target_fixture="result",
)
def run_init_vault_arg(runner, vault_arg):
    return runner.invoke(app, ["init", "--vault", vault_arg])


@when(
    parsers.parse('grid init runs with --vault "{vault_arg}" and name "{name}"'),
    target_fixture="result",
)
def run_init_vault_arg_with_name(runner, vault_arg, name):
    return runner.invoke(app, ["init", "--vault", vault_arg, "--name", name])


@then("the config file exists")
def config_file_exists(config_path):
    assert config_path.is_file()


@then("the config default matches the init path")
def config_default_matches(config_path, vault_path):
    data = tomllib.loads(config_path.read_text())
    default_name = data["default"]
    registered_path = data["vaults"][default_name]["path"]
    assert registered_path == str(vault_path.resolve())


@then("the config default is still the first vault")
def config_default_still_first(config_path):
    data = tomllib.loads(config_path.read_text())
    assert data["default"] == "first"


@then(parsers.parse('the config default is "{name}"'))
def config_default_is(config_path, name):
    data = tomllib.loads(config_path.read_text())
    assert data["default"] == name


@then("stdout contains the registered vault path")
def stdout_contains_registered_path(result, named_vault_path):
    assert str(named_vault_path) in result.stdout


@then('the resolved path is the cwd-relative "./work"')
def resolved_path_is_cwd_relative(result, cwd_dir, named_vault_path):
    expected = (cwd_dir / "work").resolve()
    assert str(expected) in result.stdout
    assert str(named_vault_path) not in result.stdout


@given("stdin is an interactive TTY")
def stdin_is_tty(monkeypatch):
    monkeypatch.setattr(
        "grid.command_routing.wizard.is_interactive", lambda: True
    )


@given("stdin is not an interactive TTY")
def stdin_is_not_tty(monkeypatch):
    monkeypatch.setattr(
        "grid.command_routing.wizard.is_interactive", lambda: False
    )


@given(
    "the platform default data directory is a fresh temp directory",
    target_fixture="platform_default_root",
)
def platform_default_root(monkeypatch, tmp_path):
    root = tmp_path / "_platform_default"
    root.mkdir()
    monkeypatch.setattr(
        "grid.command_routing.vault.user_data_path",
        lambda *args, **kwargs: root,
    )
    monkeypatch.setattr(
        "grid.command_routing.wizard.user_data_path",
        lambda *args, **kwargs: root,
    )
    return root


@when("the wizard is run choosing the default location", target_fixture="result")
def run_wizard_default_location(runner):
    # prompts: path-choice(1), name
    return runner.invoke(app, ["init"], input="1\nvault\n")


@when("the wizard is run choosing a custom path", target_fixture="result")
def run_wizard_custom_path(runner, vault_path):
    # prompts: path-choice(2), custom-path, name
    return runner.invoke(
        app, ["init"], input=f"2\n{vault_path}\n{vault_path.name}\n"
    )


@when(
    parsers.parse('the wizard is run choosing a custom path with name "{name}"'),
    target_fixture="result",
)
def run_wizard_custom_path_with_name(runner, vault_path, name):
    # prompts: path-choice(2), custom-path, name
    return runner.invoke(
        app, ["init"], input=f"2\n{vault_path}\n{name}\n"
    )


@when(
    "the wizard is run supplying an invalid then valid name", target_fixture="result"
)
def run_wizard_invalid_then_valid(runner, vault_path):
    # prompts: path-choice(2), custom-path, name(bad), name(good)
    return runner.invoke(
        app, ["init"], input=f"2\n{vault_path}\nbad name\ngood-name\n"
    )


@when(
    "the wizard is run supplying a colliding then fresh name", target_fixture="result"
)
def run_wizard_colliding_then_fresh(runner, vault_path):
    # prompts: path-choice(2), custom-path, name(collision), name(fresh), make-default
    return runner.invoke(
        app, ["init"], input=f"2\n{vault_path}\ntaken\nfresh\nn\n"
    )


@when(
    parsers.parse(
        'the wizard is run at the second path with make-default yes and name "{name}"'
    ),
    target_fixture="result",
)
def run_wizard_make_default_yes(runner, second_vault_path, name):
    # prompts: path-choice(2), custom-path, name, make-default(y)
    return runner.invoke(
        app, ["init"], input=f"2\n{second_vault_path}\n{name}\ny\n"
    )


@when(
    parsers.parse(
        'the wizard is run at the second path with make-default no and name "{name}"'
    ),
    target_fixture="result",
)
def run_wizard_make_default_no(runner, second_vault_path, name):
    # prompts: path-choice(2), custom-path, name, make-default(n)
    return runner.invoke(
        app, ["init"], input=f"2\n{second_vault_path}\n{name}\nn\n"
    )


@when(
    parsers.parse(
        'the wizard is run at that path with adopt yes and name "{name}"'
    ),
    target_fixture="result",
)
def run_wizard_adopt_yes(runner, vault_path, name):
    # prompts: path-choice(2), custom-path, name, adopt(y)
    return runner.invoke(
        app, ["init"], input=f"2\n{vault_path}\n{name}\ny\n"
    )


@when(
    parsers.parse(
        'the wizard is run at that path with adopt no and name "{name}"'
    ),
    target_fixture="result",
)
def run_wizard_adopt_no(runner, vault_path, name):
    # prompts: path-choice(2), custom-path, name, adopt(n)
    return runner.invoke(
        app, ["init"], input=f"2\n{vault_path}\n{name}\nn\n"
    )


@when(
    parsers.parse(
        'the wizard is run choosing a custom path with --name flag "{name}"'
    ),
    target_fixture="result",
)
def run_wizard_with_name_flag(runner, vault_path, name):
    # prompts: path-choice(2), custom-path (name prompt skipped by --name flag)
    return runner.invoke(
        app, ["init", "--name", name], input=f"2\n{vault_path}\n"
    )


@when(
    parsers.parse(
        'the wizard is run at the second path with --default flag and name "{name}"'
    ),
    target_fixture="result",
)
def run_wizard_with_default_flag(runner, second_vault_path, name):
    # prompts: path-choice(2), custom-path, name (make-default prompt skipped by --default)
    return runner.invoke(
        app,
        ["init", "--default"],
        input=f"2\n{second_vault_path}\n{name}\n",
    )


@when(
    parsers.parse(
        'the wizard is run at that path with --force flag and name "{name}"'
    ),
    target_fixture="result",
)
def run_wizard_with_force_flag(runner, vault_path, name):
    # prompts: path-choice(2), custom-path, name (adopt prompt skipped by --force)
    return runner.invoke(
        app, ["init", "--force"], input=f"2\n{vault_path}\n{name}\n"
    )


@then("the platform default vault directory exists")
def platform_default_vault_exists(platform_default_root):
    assert (platform_default_root / "vault").is_dir()
