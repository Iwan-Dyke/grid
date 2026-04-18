Feature: Projecting notes to RDF triples
  Notes are projected to domain Triple objects via the rdf_projection layer.
  Projection is pure — no rdflib involved — and symmetry rules are applied here.

  Scenario: Plain note emits rdf:type and identifier triples
    Given a note with id "20260409221400" and title "Alpha"
    When the note is projected to triples
    Then a triple asserts the note has rdf:type grid:Note
    And a triple asserts the note has rdf:type schema:Article
    And a triple asserts the dcterms:title is "Alpha"

  Scenario: A tag yields a skos:Concept and dcterms:subject link
    Given a note tagged "rdf"
    When the note is projected to triples
    Then a triple declares the tag is a skos:Concept
    And a triple links the note to the tag via dcterms:subject

  Scenario: linksTo is unidirectional
    Given a note with a "linksTo" link to "20260101120000"
    When the note is projected to triples
    Then a grid:linksTo triple exists from source to target
    And no grid:linksTo triple exists from target to source

  Scenario: related is symmetric
    Given a note with a "related" link to "20260101120000"
    When the note is projected to triples
    Then a skos:related triple exists from source to target
    And a skos:related triple exists from target to source

  Scenario: broader emits the narrower inverse
    Given a note with a "broader" link to "20260101120000"
    When the note is projected to triples
    Then a skos:broader triple exists from source to target
    And a skos:narrower triple exists from target to source

  Scenario: Custom link types use the grid namespace
    Given a note with a "inspiredBy" link to "20260101120000"
    When the note is projected to triples
    Then a grid:inspiredBy triple exists from source to target

  Scenario: A link to a note not in the input list is still projected
    Given a note with a "linksTo" link to a dangling target "99999999999999"
    When the note is projected to triples
    Then a grid:linksTo triple exists from source to the dangling target
    And the dangling target is not asserted to be a grid:Note
