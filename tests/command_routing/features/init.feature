Feature: grid init
  The init command creates or adopts a vault directory, following the shared
  vault resolution rules and reporting the absolute vault path.

  Scenario: Fresh path is created
    Given a vault path that does not exist
    When grid init runs with that --vault path
    Then the directory exists
    And stdout contains "Initialised"
    And stdout contains the absolute vault path
    And the exit code is 0

  Scenario: Empty directory is adopted idempotently
    Given an empty vault directory
    When grid init runs with that --vault path
    Then stdout contains "already exists"
    And stdout contains the absolute vault path
    And the exit code is 0

  Scenario: Existing grid vault is idempotent
    Given a vault directory containing a grid-style note
    When grid init runs with that --vault path
    Then stdout contains "already exists"
    And stdout contains the absolute vault path
    And the exit code is 0

  Scenario: Non-grid content without --force is rejected
    Given a vault directory containing a non-grid file
    When grid init runs with that --vault path
    Then stderr contains "not empty"
    And stderr contains "--force"
    And stderr contains the absolute vault path
    And the exit code is 1

  Scenario: Non-grid content with --force is adopted
    Given a vault directory containing a non-grid file
    When grid init runs with that --vault path and --force
    Then stdout contains "Initialised"
    And stdout contains the absolute vault path
    And the non-grid file still exists
    And the exit code is 0

  Scenario: Hidden files do not count as content
    Given a vault directory containing only hidden entries
    When grid init runs with that --vault path
    Then stdout contains "already exists"
    And stdout contains the absolute vault path
    And the exit code is 0

  Scenario: Path pointing at a file errors
    Given a path that points at an existing file
    When grid init runs with that --vault path
    Then stderr contains "not a directory"
    And stderr contains the absolute vault path
    And the exit code is 1

  Scenario: Forcing does not override the file-at-path error
    Given a path that points at an existing file
    When grid init runs with that --vault path and --force
    Then stderr contains "not a directory"
    And stderr contains the absolute vault path
    And the exit code is 1

  Scenario: --vault takes precedence over GRID_VAULT
    Given GRID_VAULT is set to a path that does not exist
    And a different vault path that does not exist
    When grid init runs with the different path via --vault
    Then the different path exists
    And the GRID_VAULT path does not exist
    And stdout contains the different absolute path
    And the exit code is 0

  Scenario: GRID_VAULT is used when --vault is absent
    Given GRID_VAULT is set to a path that does not exist
    When grid init runs with no --vault flag
    Then the GRID_VAULT path exists
    And stdout contains the GRID_VAULT absolute path
    And stdout contains "Initialised"
    And the exit code is 0

  Scenario: Missing parent directories are created
    Given a vault path with missing parent directories
    When grid init runs with that --vault path
    Then the directory exists
    And stdout contains "Initialised"
    And stdout contains the absolute vault path
    And the exit code is 0

  Scenario: First init writes config with the vault as default
    Given a vault path that does not exist
    When grid init runs with that --vault path
    Then the config file exists
    And the config default matches the init path
    And the exit code is 0

  Scenario: Second init without --default preserves existing default
    Given a first vault is already registered as default
    And a second vault path that does not exist
    When grid init runs with the second vault path and name "second"
    Then the config default is still the first vault
    And the exit code is 0

  Scenario: Second init with --default switches default
    Given a first vault is already registered as default
    And a second vault path that does not exist
    When grid init runs with the second vault path and name "second" and --default
    Then the config default is "second"
    And the exit code is 0

  Scenario: Re-init on a registered path is idempotent
    Given a vault is registered at a path
    When grid init runs with that registered path again
    Then stdout contains "already registered as"
    And the exit code is 0

  Scenario: --name is ignored when path is already registered
    Given a vault named "foo" is registered at a path
    When grid init runs with that registered path and name "bar"
    Then stdout contains "already registered as 'foo'"
    And the exit code is 0

  Scenario: Name collision at different path errors
    Given a vault named "foo" is registered at a path
    And a different vault path that does not exist
    When grid init runs with the different path and name "foo"
    Then stderr contains "already exists at a different path"
    And the exit code is 1

  Scenario: --vault with a registered name resolves to that vault's path
    Given a vault named "work" is registered at a path
    When grid init runs with --vault "work"
    Then stdout contains the registered vault path
    And the exit code is 0

  Scenario: --vault with leading ./ bypasses name lookup
    Given a vault named "work" is registered at a path
    And the working directory is a fresh temp directory
    When grid init runs with --vault "./work" and name "local"
    Then the resolved path is the cwd-relative "./work"
    And the exit code is 0

  Scenario: Wizard: default location chosen
    Given stdin is an interactive TTY
    And the platform default data directory is a fresh temp directory
    When the wizard is run choosing the default location
    Then the platform default vault directory exists
    And stdout contains "Initialised"
    And the exit code is 0

  Scenario: Wizard: custom path chosen
    Given stdin is an interactive TTY
    And a vault path that does not exist
    When the wizard is run choosing a custom path
    Then the directory exists
    And stdout contains "Initialised"
    And stdout contains the absolute vault path
    And the exit code is 0

  Scenario: Wizard accepts valid name
    Given stdin is an interactive TTY
    And a vault path that does not exist
    When the wizard is run choosing a custom path with name "my-vault"
    Then stdout contains "Registered vault 'my-vault'"
    And the exit code is 0

  Scenario: Wizard re-prompts on invalid name
    Given stdin is an interactive TTY
    And a vault path that does not exist
    When the wizard is run supplying an invalid then valid name
    Then stderr contains "Invalid vault name"
    And stdout contains "Registered vault 'good-name'"
    And the exit code is 0

  Scenario: Wizard re-prompts on name collision
    Given a vault named "taken" is registered at a path
    And stdin is an interactive TTY
    And a different vault path that does not exist
    When the wizard is run supplying a colliding then fresh name
    Then stderr contains "already exists at a different path"
    And stdout contains "Registered vault 'fresh'"
    And the exit code is 0

  Scenario: Wizard make-default answered yes switches default
    Given a first vault is already registered as default
    And stdin is an interactive TTY
    And a second vault path that does not exist
    When the wizard is run at the second path with make-default yes and name "second"
    Then the config default is "second"
    And the exit code is 0

  Scenario: Wizard make-default answered no preserves existing default
    Given a first vault is already registered as default
    And stdin is an interactive TTY
    And a second vault path that does not exist
    When the wizard is run at the second path with make-default no and name "second"
    Then the config default is still the first vault
    And the exit code is 0

  Scenario: Wizard adopt answered yes adopts non-grid content
    Given stdin is an interactive TTY
    And a vault directory containing a non-grid file
    When the wizard is run at that path with adopt yes and name "adopted"
    Then stdout contains "Initialised"
    And the non-grid file still exists
    And the exit code is 0

  Scenario: Wizard adopt answered no rejects with error
    Given stdin is an interactive TTY
    And a vault directory containing a non-grid file
    When the wizard is run at that path with adopt no and name "rejected"
    Then stderr contains "not empty"
    And the exit code is 1

  Scenario: Wizard does not activate when --vault is passed
    Given stdin is an interactive TTY
    And a vault path that does not exist
    When grid init runs with that --vault path
    Then stdout contains "Initialised"
    And stdout contains the absolute vault path
    And the exit code is 0

  Scenario: Wizard does not activate when stdin is not a TTY
    Given stdin is not an interactive TTY
    And the platform default data directory is a fresh temp directory
    When grid init runs with no --vault flag
    Then the platform default vault directory exists
    And stdout contains "Initialised"
    And the exit code is 0

  Scenario: Wizard skips name prompt when --name is passed
    Given stdin is an interactive TTY
    And a vault path that does not exist
    When the wizard is run choosing a custom path with --name flag "flagname"
    Then stdout contains "Registered vault 'flagname'"
    And the exit code is 0

  Scenario: Wizard skips default prompt when --default is passed
    Given a first vault is already registered as default
    And stdin is an interactive TTY
    And a second vault path that does not exist
    When the wizard is run at the second path with --default flag and name "second"
    Then the config default is "second"
    And the exit code is 0

  Scenario: Wizard skips adopt prompt when --force is passed
    Given stdin is an interactive TTY
    And a vault directory containing a non-grid file
    When the wizard is run at that path with --force flag and name "forced"
    Then stdout contains "Initialised"
    And the non-grid file still exists
    And the exit code is 0
