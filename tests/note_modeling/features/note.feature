Feature: Note value object
  Notes are immutable value objects representing knowledge graph entries.

  Scenario: Create a valid note
    Given a valid note with title "My Note"
    When the note is created
    Then the note title is "My Note"
    And the note type is "note"

  Scenario: Empty title is rejected
    Given a note with an empty title
    When the note is created
    Then a ValueError is raised

  Scenario: Modified before created is rejected
    Given a note where modified is before created
    When the note is created
    Then a ValueError is raised

  Scenario: Note with tags and links
    Given a note with tags "rdf, linked-data" and a link to "20260101120000"
    When the note is created
    Then the note has 2 tags
    And the note has 1 link
