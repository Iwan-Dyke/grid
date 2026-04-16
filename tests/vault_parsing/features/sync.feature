Feature: Sync wiki-links to frontmatter
  Sync parses body wiki-links and replaces the links array in frontmatter.
  Body is the single source of truth for links.

  Scenario: Links extracted from body replace frontmatter links
    Given a note with body "See [[20260101120000]]" and no frontmatter links
    When the note is synced
    Then the note has 1 link to "20260101120000"

  Scenario: Unchanged links return original note
    Given a note with body "See [[20260101120000]]" and matching frontmatter links
    When the note is synced
    Then the original note is returned unchanged

  Scenario: Removed body link removes frontmatter link
    Given a note with body "No links here" and a frontmatter link to "20260101120000"
    When the note is synced
    Then the note has 0 links

  Scenario: Modified timestamp updates when links change
    Given a note with body "See [[20260101120000]]" and no frontmatter links
    When the note is synced
    Then the modified timestamp is updated

  Scenario: Modified timestamp unchanged when links match
    Given a note with body "See [[20260101120000]]" and matching frontmatter links
    When the note is synced
    Then the modified timestamp is unchanged
