from grid.note_modeling import Link, Tag, Triple
from grid.rdf_projection import DEFAULT_GRID_URI, project

from tests.rdf_projection.conftest import make_note


GRID = DEFAULT_GRID_URI
RDF_TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
SKOS = "http://www.w3.org/2004/02/skos/core#"
RDFS = "http://www.w3.org/2000/01/rdf-schema#"
DCTERMS = "http://purl.org/dc/terms/"
SCHEMA = "https://schema.org/"


def _subject_triples(triples, subject):
    return [t for t in triples if t.subject == subject]


class TestNoteProjection:
    def test_emits_rdf_type_grid_note(self):
        triples = project([make_note(id="20260409221400")], GRID)
        subject = f"{GRID}20260409221400"
        assert Triple(subject, RDF_TYPE, f"{GRID}Note") in triples

    def test_emits_rdf_type_schema_article(self):
        triples = project([make_note(id="20260409221400")], GRID)
        subject = f"{GRID}20260409221400"
        assert Triple(subject, RDF_TYPE, f"{SCHEMA}Article") in triples

    def test_emits_dcterms_identifier(self):
        triples = project([make_note(id="20260409221400")], GRID)
        subject = f"{GRID}20260409221400"
        assert Triple(subject, f"{DCTERMS}identifier", "20260409221400") in triples

    def test_emits_dcterms_title(self):
        triples = project([make_note(title="My Title")], GRID)
        matching = [t for t in triples if t.predicate == f"{DCTERMS}title"]
        assert any(t.object == "My Title" for t in matching)

    def test_emits_created_and_modified(self):
        triples = project([make_note()], GRID)
        predicates = {t.predicate for t in triples}
        assert f"{DCTERMS}created" in predicates
        assert f"{DCTERMS}modified" in predicates

    def test_created_is_typed_literal_with_datetime(self):
        from grid.note_modeling import TypedLiteral

        triples = project([make_note()], GRID)
        created = next(t for t in triples if t.predicate == f"{DCTERMS}created")
        assert isinstance(created.object, TypedLiteral)
        assert created.object.datatype.endswith("#dateTime")

    def test_modified_is_typed_literal_with_datetime(self):
        from grid.note_modeling import TypedLiteral

        triples = project([make_note()], GRID)
        modified = next(t for t in triples if t.predicate == f"{DCTERMS}modified")
        assert isinstance(modified.object, TypedLiteral)
        assert modified.object.datatype.endswith("#dateTime")

    def test_title_is_plain_str_not_typed_literal(self):
        from grid.note_modeling import TypedLiteral

        triples = project([make_note()], GRID)
        title = next(t for t in triples if t.predicate == f"{DCTERMS}title")
        assert not isinstance(title.object, TypedLiteral)


class TestTagProjection:
    def test_emits_skos_concept(self):
        note = make_note(tags=(Tag(name="rdf"),))
        triples = project([note], GRID)
        tag_iri = f"{GRID}tag-rdf"
        assert Triple(tag_iri, RDF_TYPE, f"{SKOS}Concept") in triples

    def test_emits_pref_label(self):
        note = make_note(tags=(Tag(name="rdf"),))
        triples = project([note], GRID)
        tag_iri = f"{GRID}tag-rdf"
        assert Triple(tag_iri, f"{SKOS}prefLabel", "rdf") in triples

    def test_links_note_to_tag(self):
        note = make_note(id="20260409221400", tags=(Tag(name="rdf"),))
        triples = project([note], GRID)
        assert (
            Triple(
                f"{GRID}20260409221400",
                f"{DCTERMS}subject",
                f"{GRID}tag-rdf",
            )
            in triples
        )

    def test_hyphenated_tag_produces_valid_iri(self):
        note = make_note(tags=(Tag(name="linked-data"),))
        triples = project([note], GRID)
        assert any(t.subject == f"{GRID}tag-linked-data" for t in triples)


class TestLinkProjection:
    def _source_target(self):
        return (
            f"{GRID}20260409221400",
            f"{GRID}20260101120000",
        )

    def test_links_to_is_unidirectional(self):
        source, target = self._source_target()
        note = make_note(links=(Link(target_id="20260101120000", link_type="linksTo"),))
        triples = project([note], GRID)
        assert Triple(source, f"{GRID}linksTo", target) in triples
        assert Triple(target, f"{GRID}linksTo", source) not in triples

    def test_related_is_symmetric(self):
        source, target = self._source_target()
        note = make_note(links=(Link(target_id="20260101120000", link_type="related"),))
        triples = project([note], GRID)
        assert Triple(source, f"{SKOS}related", target) in triples
        assert Triple(target, f"{SKOS}related", source) in triples

    def test_broader_emits_inverse_narrower(self):
        source, target = self._source_target()
        note = make_note(links=(Link(target_id="20260101120000", link_type="broader"),))
        triples = project([note], GRID)
        assert Triple(source, f"{SKOS}broader", target) in triples
        assert Triple(target, f"{SKOS}narrower", source) in triples

    def test_narrower_emits_inverse_broader(self):
        source, target = self._source_target()
        note = make_note(
            links=(Link(target_id="20260101120000", link_type="narrower"),)
        )
        triples = project([note], GRID)
        assert Triple(source, f"{SKOS}narrower", target) in triples
        assert Triple(target, f"{SKOS}broader", source) in triples

    def test_see_also_is_unidirectional(self):
        source, target = self._source_target()
        note = make_note(links=(Link(target_id="20260101120000", link_type="seeAlso"),))
        triples = project([note], GRID)
        assert Triple(source, f"{RDFS}seeAlso", target) in triples
        assert Triple(target, f"{RDFS}seeAlso", source) not in triples

    def test_custom_link_type_uses_grid_namespace(self):
        source, target = self._source_target()
        note = make_note(
            links=(Link(target_id="20260101120000", link_type="inspiredBy"),)
        )
        triples = project([note], GRID)
        assert Triple(source, f"{GRID}inspiredBy", target) in triples
        assert Triple(target, f"{GRID}inspiredBy", source) not in triples

    def test_label_is_not_projected(self):
        note = make_note(
            links=(
                Link(target_id="20260101120000", link_type="related", label="see this"),
            ),
        )
        triples = project([note], GRID)
        assert not any("see this" in t.object for t in triples)


class TestCustomGridUri:
    def test_honours_custom_grid_uri(self):
        custom = "https://example.org/mygrid/"
        note = make_note(id="20260409221400")
        triples = project([note], custom)
        assert Triple(f"{custom}20260409221400", RDF_TYPE, f"{custom}Note") in triples


class TestDanglingLinks:
    def test_dangling_target_is_still_projected(self):
        note = make_note(
            id="20260409221400",
            links=(Link(target_id="99999999999999", link_type="linksTo"),),
        )
        triples = project([note], GRID)
        assert (
            Triple(
                f"{GRID}20260409221400",
                f"{GRID}linksTo",
                f"{GRID}99999999999999",
            )
            in triples
        )

    def test_dangling_target_is_not_asserted_as_grid_note(self):
        note = make_note(
            id="20260409221400",
            links=(Link(target_id="99999999999999", link_type="linksTo"),),
        )
        triples = project([note], GRID)
        assert Triple(f"{GRID}99999999999999", RDF_TYPE, f"{GRID}Note") not in triples
