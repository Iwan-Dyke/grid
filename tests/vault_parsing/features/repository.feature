Feature: Markdown file repository
  The repository reads and writes notes as markdown files in a flat directory.

  Scenario: Save and load a note
    Given an empty vault
    When I save a note with title "My Note"
    And I load the note by ID
    Then the loaded note has title "My Note"

  Scenario: Load all notes
    Given a vault with 3 notes
    When I load all notes
    Then 3 notes are returned

  Scenario: Delete a note
    Given a vault with a saved note
    When I delete the note
    Then the note no longer exists

  Scenario: Check existence
    Given a vault with a saved note
    Then the note exists
    And a nonexistent note does not exist

  Scenario: Load raw file contents
    Given a vault with a saved note
    When I load the raw contents
    Then the raw contents contain frontmatter and body

  Scenario: Load nonexistent note raises error
    Given an empty vault
    When I load a nonexistent note
    Then a NoteNotFoundError is raised

  Scenario: Malformed frontmatter raises error
    Given a vault with a malformed markdown file
    When I load all notes
    Then a NoteParseError is raised
