Feature: Service orchestration
  The service layer coordinates note_modeling, vault_parsing, and rdf_projection.
  It reconciles body wiki-links to frontmatter on every read and supports
  note creation, linking, search, listing, and RDF export.

  Scenario: Loading the vault reconciles body links into frontmatter
    Given a vault with a note whose body contains "[[20260101120000]]"
    When the vault is loaded
    Then the note in the graph has 1 link
    And the reconciled note is written to disk

  Scenario: Creating a note persists it to the vault
    Given an empty vault
    When a note is created with title "Hello"
    Then the note exists in the vault
    And the note has a 14-digit ID

  Scenario: Adding a link appends to body and updates frontmatter
    Given a vault with a note whose body is empty
    When a "related" link to "20260101120000" is added
    Then the body contains "[[related::20260101120000]]"
    And the frontmatter links contain "20260101120000"

  Scenario: Syncing the vault reconciles every note
    Given a vault with a note whose body contains "[[20260101120000]]"
    When the vault is synced
    Then every returned note is reconciled

  Scenario: Search finds notes by title
    Given a graph with a note titled "Python Basics"
    When the graph is searched for "python"
    Then the matching note is returned

  Scenario: List filters by tag and type
    Given a graph with notes with different tags and types
    When listing notes with tag "rdf" and type "reference"
    Then only the matching note is returned

  Scenario: Export produces RDF turtle
    Given a graph with a note
    When the graph is exported as turtle
    Then the output contains the note ID
