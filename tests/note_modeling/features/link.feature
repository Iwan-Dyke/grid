Feature: Link validation
  Links are immutable value objects representing typed relationships between notes.

  Scenario: Valid link with default type
    Given a link to "20260409221400" with type "linksTo"
    When the link is created
    Then the link target is "20260409221400"
    And the link type is "linksTo"
    And the link label is empty

  Scenario: Valid link with label
    Given a link to "20260409221400" with type "related" and label "see this"
    When the link is created
    Then the link label is "see this"

  Scenario: Invalid target ID rejected
    Given a link to "not-an-id" with type "linksTo"
    When the link is created
    Then a ValueError is raised

  Scenario: Empty target ID rejected
    Given a link to "" with type "linksTo"
    When the link is created
    Then a ValueError is raised

  Scenario: Empty link type rejected
    Given a link to "20260409221400" with type ""
    When the link is created
    Then a ValueError is raised

  Scenario: Custom link type accepted
    Given a link to "20260409221400" with type "inspiredBy"
    When the link is created
    Then the link type is "inspiredBy"
