Feature: Tag validation
  Tags are immutable value objects with enforced naming constraints.

  Scenario: Valid tag is lowercased
    Given a tag name "RDF"
    When the tag is created
    Then the tag name is "rdf"

  Scenario: Whitespace is rejected
    Given a tag name "linked data"
    When the tag is created
    Then a ValueError is raised

  Scenario: Empty string is rejected
    Given a tag name ""
    When the tag is created
    Then a ValueError is raised

  Scenario: Tag exceeds max length
    Given a tag name that is 51 characters long
    When the tag is created
    Then a ValueError is raised

  Scenario: Tag at max length is accepted
    Given a tag name that is 50 characters long
    When the tag is created
    Then the tag is created successfully

  Scenario: Leading and trailing whitespace is stripped
    Given a tag name "  rdf  "
    When the tag is created
    Then the tag name is "rdf"

  Scenario: Interior whitespace is still rejected after stripping
    Given a tag name "  linked data  "
    When the tag is created
    Then a ValueError is raised
