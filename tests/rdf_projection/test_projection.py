from pytest_bdd import scenario, given, when, then, parsers

from grid.note_modeling import Link, Tag, Triple
from grid.rdf_projection import DEFAULT_GRID_URI, project

from tests.rdf_projection.conftest import make_note


GRID = DEFAULT_GRID_URI
RDF_TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
SKOS = "http://www.w3.org/2004/02/skos/core#"
SCHEMA = "https://schema.org/"
DCTERMS = "http://purl.org/dc/terms/"

SOURCE_ID = "20260409221400"
TARGET_ID = "20260101120000"


@scenario("features/projection.feature", "Plain note emits rdf:type and identifier triples")
def test_plain_note():
    pass


@scenario("features/projection.feature", "A tag yields a skos:Concept and dcterms:subject link")
def test_tag_projection():
    pass


@scenario("features/projection.feature", "linksTo is unidirectional")
def test_links_to_unidirectional():
    pass


@scenario("features/projection.feature", "related is symmetric")
def test_related_symmetric():
    pass


@scenario("features/projection.feature", "broader emits the narrower inverse")
def test_broader_inverse():
    pass


@scenario("features/projection.feature", "Custom link types use the grid namespace")
def test_custom_link_type():
    pass


@scenario(
    "features/projection.feature",
    "A link to a note not in the input list is still projected",
)
def test_dangling_link():
    pass


DANGLING_ID = "99999999999999"


@given(
    parsers.parse('a note with id "{note_id}" and title "{title}"'),
    target_fixture="note",
)
def note_with_id_and_title(note_id, title):
    return make_note(id=note_id, title=title)


@given(parsers.parse('a note tagged "{tag}"'), target_fixture="note")
def note_with_tag(tag):
    return make_note(id=SOURCE_ID, tags=(Tag(name=tag),))


@given(
    parsers.parse('a note with a "{link_type}" link to "{target}"'),
    target_fixture="note",
)
def note_with_link(link_type, target):
    return make_note(
        id=SOURCE_ID,
        links=(Link(target_id=target, link_type=link_type),),
    )


@when("the note is projected to triples", target_fixture="triples")
def project_note(note):
    return project([note], GRID)


@then("a triple asserts the note has rdf:type grid:Note")
def check_grid_note(triples):
    assert Triple(f"{GRID}{SOURCE_ID}", RDF_TYPE, f"{GRID}Note") in triples


@then("a triple asserts the note has rdf:type schema:Article")
def check_schema_article(triples):
    assert Triple(f"{GRID}{SOURCE_ID}", RDF_TYPE, f"{SCHEMA}Article") in triples


@then(parsers.parse('a triple asserts the dcterms:title is "{title}"'))
def check_title(triples, title):
    assert any(
        t.predicate == f"{DCTERMS}title" and t.object == title for t in triples
    )


@then("a triple declares the tag is a skos:Concept")
def check_tag_concept(triples):
    assert any(
        t.predicate == RDF_TYPE and t.object == f"{SKOS}Concept" for t in triples
    )


@then("a triple links the note to the tag via dcterms:subject")
def check_tag_subject(triples):
    assert any(
        t.subject == f"{GRID}{SOURCE_ID}" and t.predicate == f"{DCTERMS}subject"
        for t in triples
    )


@then("a grid:linksTo triple exists from source to target")
def check_links_to_forward(triples):
    assert Triple(f"{GRID}{SOURCE_ID}", f"{GRID}linksTo", f"{GRID}{TARGET_ID}") in triples


@then("no grid:linksTo triple exists from target to source")
def check_links_to_no_reverse(triples):
    assert Triple(f"{GRID}{TARGET_ID}", f"{GRID}linksTo", f"{GRID}{SOURCE_ID}") not in triples


@then("a skos:related triple exists from source to target")
def check_related_forward(triples):
    assert Triple(f"{GRID}{SOURCE_ID}", f"{SKOS}related", f"{GRID}{TARGET_ID}") in triples


@then("a skos:related triple exists from target to source")
def check_related_reverse(triples):
    assert Triple(f"{GRID}{TARGET_ID}", f"{SKOS}related", f"{GRID}{SOURCE_ID}") in triples


@then("a skos:broader triple exists from source to target")
def check_broader_forward(triples):
    assert Triple(f"{GRID}{SOURCE_ID}", f"{SKOS}broader", f"{GRID}{TARGET_ID}") in triples


@then("a skos:narrower triple exists from target to source")
def check_narrower_inverse(triples):
    assert Triple(f"{GRID}{TARGET_ID}", f"{SKOS}narrower", f"{GRID}{SOURCE_ID}") in triples


@then("a grid:inspiredBy triple exists from source to target")
def check_custom_forward(triples):
    assert Triple(
        f"{GRID}{SOURCE_ID}", f"{GRID}inspiredBy", f"{GRID}{TARGET_ID}"
    ) in triples


@given(
    parsers.parse(
        'a note with a "{link_type}" link to a dangling target "{target}"'
    ),
    target_fixture="note",
)
def note_with_dangling_link(link_type, target):
    return make_note(
        id=SOURCE_ID,
        links=(Link(target_id=target, link_type=link_type),),
    )


@then("a grid:linksTo triple exists from source to the dangling target")
def check_dangling_projected(triples):
    assert Triple(
        f"{GRID}{SOURCE_ID}", f"{GRID}linksTo", f"{GRID}{DANGLING_ID}"
    ) in triples


@then("the dangling target is not asserted to be a grid:Note")
def check_dangling_not_typed(triples):
    assert Triple(f"{GRID}{DANGLING_ID}", RDF_TYPE, f"{GRID}Note") not in triples
