Feature: Graph traversal
  The graph is a mutable container for notes with traversal capabilities.

  Scenario: Add and retrieve a note
    Given a graph with a note "20260409221400" titled "First Note"
    When I get note "20260409221400"
    Then the result is "First Note"

  Scenario: Get returns nothing for unknown ID
    Given an empty graph
    When I get note "20260409221400"
    Then the result is empty

  Scenario: Outgoing links
    Given a graph where "A" links to "B" and "C"
    When I ask for outgoing from "A"
    Then the result contains "B" and "C"

  Scenario: Incoming links
    Given a graph where "A" links to "B" and "C"
    When I ask for incoming to "B"
    Then the result contains "A"

  Scenario: Neighbors returns both directions
    Given a graph where "A" links to "B" and "C" links to "A"
    When I ask for neighbors of "A"
    Then the result contains "B" and "C"

  Scenario: Filter by tag
    Given a graph with notes tagged "rdf" and "python"
    When I filter by tag "rdf"
    Then only notes tagged "rdf" are returned
