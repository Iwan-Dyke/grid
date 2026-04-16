Feature: Wiki-link extraction
  Wiki-links in note bodies are parsed into Link value objects.

  Scenario: Plain link
    Given a body containing "See [[20260409221400]] for details"
    When wiki-links are extracted
    Then 1 link is found
    And the link has target "20260409221400" and type "linksTo" and no label

  Scenario: Typed link
    Given a body containing "See [[related::20260409221400]] for details"
    When wiki-links are extracted
    Then 1 link is found
    And the link has target "20260409221400" and type "related" and no label

  Scenario: Typed link with label
    Given a body containing "See [[related::20260409221400|see this]] for details"
    When wiki-links are extracted
    Then 1 link is found
    And the link has target "20260409221400" and type "related" and label "see this"

  Scenario: Multiple links in one body
    Given a body containing "[[20260409221400]] and [[broader::20260101120000]]"
    When wiki-links are extracted
    Then 2 links are found

  Scenario: No links in body
    Given a body containing "Just plain text"
    When wiki-links are extracted
    Then 0 links are found

  Scenario: Label without type is ambiguous
    Given a body containing "[[20260409221400|some label]]"
    When wiki-links are extracted
    Then 1 link is found
    And the link has target "20260409221400" and type "linksTo" and no label
    And the ambiguity is flagged
