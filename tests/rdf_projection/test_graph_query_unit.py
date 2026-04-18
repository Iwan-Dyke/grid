from grid.note_modeling import GraphQuery, Link, Tag
from grid.rdf_projection import DEFAULT_GRID_URI, RDFlibGraphQuery

from tests.rdf_projection.conftest import make_note


class TestProtocolConformance:
    def test_satisfies_graph_query(self):
        assert isinstance(RDFlibGraphQuery(), GraphQuery)


class TestBuild:
    def test_returns_triples(self):
        q = RDFlibGraphQuery()
        triples = q.build([make_note()])
        assert len(triples) > 0

    def test_empty_input(self):
        q = RDFlibGraphQuery()
        assert q.build([]) == []


class TestSerialize:
    def test_turtle_output(self):
        q = RDFlibGraphQuery()
        q.build([make_note(id="20260409221400", title="Hello")])
        output = q.serialize(format="turtle")
        assert "20260409221400" in output
        assert "Hello" in output

    def test_serialize_before_build_does_not_raise(self):
        q = RDFlibGraphQuery()
        q.serialize(format="turtle")

    def test_ntriples_output(self):
        q = RDFlibGraphQuery()
        q.build([make_note(id="20260409221400", title="Hello")])
        output = q.serialize(format="nt")
        assert "20260409221400" in output


class TestSparql:
    def test_select_notes(self):
        q = RDFlibGraphQuery()
        q.build([
            make_note(id="20260409221400", title="A"),
            make_note(id="20260101120000", title="B"),
        ])
        results = q.query("SELECT ?s WHERE { ?s a grid:Note } ORDER BY ?s")
        ids = [r["s"] for r in results]
        assert f"{DEFAULT_GRID_URI}20260101120000" in ids
        assert f"{DEFAULT_GRID_URI}20260409221400" in ids

    def test_skos_prefix_auto_injected(self):
        q = RDFlibGraphQuery()
        q.build([make_note(tags=(Tag(name="rdf"),))])
        results = q.query("SELECT ?c WHERE { ?c a skos:Concept }")
        assert len(results) == 1

    def test_user_prefix_overrides(self):
        q = RDFlibGraphQuery()
        q.build([make_note(tags=(Tag(name="rdf"),))])
        sparql = (
            "PREFIX skos: <http://www.w3.org/2004/02/skos/core#> "
            "SELECT ?c WHERE { ?c a skos:Concept }"
        )
        results = q.query(sparql)
        assert len(results) == 1

    def test_query_literal_returns_python_value(self):
        q = RDFlibGraphQuery()
        q.build([make_note(id="20260409221400", title="Hello")])
        results = q.query(
            "SELECT ?t WHERE { ?s <http://purl.org/dc/terms/title> ?t }"
        )
        assert results[0]["t"] == "Hello"


class TestExtensibility:
    def test_custom_grid_uri_used_in_triples(self):
        custom = "https://mygrid.example/ns/"
        q = RDFlibGraphQuery(grid_uri=custom)
        q.build([make_note(id="20260409221400")])
        output = q.serialize(format="turtle")
        assert custom in output

    def test_extra_namespace_included_in_prefixes(self):
        q = RDFlibGraphQuery(
            extra_namespaces={"foaf": "http://xmlns.com/foaf/0.1/"},
        )
        assert q.prefixes["foaf"] == "http://xmlns.com/foaf/0.1/"

    def test_builtin_prefixes_always_present(self):
        q = RDFlibGraphQuery()
        for prefix in ("grid", "skos", "schema", "dcterms", "rdfs", "xsd"):
            assert prefix in q.prefixes

    def test_extra_namespace_resolves_in_sparql(self):
        q = RDFlibGraphQuery(
            extra_namespaces={"zz": "https://example.invalid/zz/"},
        )
        q.build([make_note()])
        results = q.query("SELECT ?x WHERE { BIND(zz:Thing AS ?x) }")
        assert results[0]["x"] == "https://example.invalid/zz/Thing"

    def test_unregistered_prefix_fails_to_resolve(self):
        q = RDFlibGraphQuery()
        q.build([make_note()])
        raised = False
        try:
            q.query("SELECT ?x WHERE { BIND(zzunknown:Thing AS ?x) }")
        except Exception:
            raised = True
        assert raised


class TestIRIMarker:
    def test_title_containing_url_is_treated_as_literal(self):
        q = RDFlibGraphQuery()
        q.build([make_note(title="See http://example.com for details")])
        output = q.serialize(format="nt")
        assert '"See http://example.com for details"' in output

    def test_title_containing_url_is_queryable_as_literal(self):
        q = RDFlibGraphQuery()
        q.build([make_note(id="20260409221400", title="See http://example.com")])
        results = q.query(
            "SELECT ?t WHERE { ?s <http://purl.org/dc/terms/title> ?t }"
        )
        assert results[0]["t"] == "See http://example.com"


class TestProjectionIRIMarking:
    def test_projected_link_target_is_marked_iri(self):
        from grid.note_modeling import IRI, Link
        from grid.rdf_projection import project

        note = make_note(
            id="20260409221400",
            links=(Link(target_id="20260101120000", link_type="linksTo"),),
        )
        triples = project([note], DEFAULT_GRID_URI)
        link_triple = next(t for t in triples if "linksTo" in t.predicate)
        assert isinstance(link_triple.object, IRI)

    def test_projected_title_is_plain_str(self):
        from grid.note_modeling import IRI
        from grid.rdf_projection import project

        triples = project([make_note(title="Plain Title")], DEFAULT_GRID_URI)
        title_triple = next(
            t for t in triples if t.predicate.endswith("title")
        )
        assert not isinstance(title_triple.object, IRI)


class TestSymmetryInGraph:
    def test_related_link_queryable_from_either_side(self):
        q = RDFlibGraphQuery()
        q.build([
            make_note(
                id="20260409221400",
                links=(Link(target_id="20260101120000", link_type="related"),),
            ),
        ])
        forward = q.query(
            f"SELECT ?o WHERE {{ <{DEFAULT_GRID_URI}20260409221400> skos:related ?o }}"
        )
        backward = q.query(
            f"SELECT ?o WHERE {{ <{DEFAULT_GRID_URI}20260101120000> skos:related ?o }}"
        )
        assert len(forward) == 1
        assert len(backward) == 1
