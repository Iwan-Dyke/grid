Feature: Parsing markdown notes into Note value objects
  parse_note reads a markdown file with YAML frontmatter and returns a Note.
  Timestamps are normalized to UTC regardless of the stored offset.

  Scenario: Round-trip preserves all fields
    Given a Note serialized to a markdown file
    When I parse the file
    Then the loaded note equals the original

  Scenario: Missing id raises a parse error
    Given a markdown file with frontmatter "title: Test\n"
    When I parse the file
    Then a NoteParseError is raised

  Scenario: Missing title raises a parse error
    Given a markdown file with frontmatter "id: '20260409221400'\n"
    When I parse the file
    Then a NoteParseError is raised

  Scenario: A non-UTC timestamp is converted to UTC
    Given a markdown file with created timestamp "2026-04-09T22:14:00+02:00"
    When I parse the file
    Then the loaded note's created timestamp is "2026-04-09T20:14:00+00:00"

  Scenario: A naive timestamp is tagged as UTC
    Given a markdown file with created timestamp "2026-04-09T22:14:00"
    When I parse the file
    Then the loaded note's created timestamp is "2026-04-09T22:14:00+00:00"
