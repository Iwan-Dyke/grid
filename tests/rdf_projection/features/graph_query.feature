Feature: Querying and serializing RDF via rdflib
  RDFlibGraphQuery builds an in-memory rdflib graph from notes, answers SPARQL
  queries with auto-injected prefixes, and serializes to standard formats.

  Scenario: SPARQL query with built-in prefix finds notes
    Given a graph query built from 2 notes
    When I run the SPARQL query "SELECT ?s WHERE { ?s a grid:Note }"
    Then 2 results are returned

  Scenario: Serializing to Turtle includes the note identifier
    Given a graph query built from 1 note with id "20260409221400"
    When I serialize the graph to "turtle"
    Then the output contains "20260409221400"

  Scenario: Custom grid URI is used in the serialized output
    Given a graph query using grid URI "https://mygrid.example/ns/" built from 1 note
    When I serialize the graph to "turtle"
    Then the output contains "https://mygrid.example/ns/"

  Scenario: Extra namespaces are registered as prefixes
    Given a graph query with extra namespace "foaf" bound to "http://xmlns.com/foaf/0.1/"
    Then the prefixes include "foaf"
