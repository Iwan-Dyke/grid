from datetime import datetime, UTC

from pytest_bdd import scenario, given, when, then, parsers

from grid.note_modeling.graph import Graph
from grid.note_modeling.note import Note
from grid.note_modeling.tag import Tag
from grid.note_modeling.link import Link


NOW = datetime(2026, 4, 9, 22, 14, 0, tzinfo=UTC)

IDS = {
    "A": "20260409221400",
    "B": "20260409221401",
    "C": "20260409221402",
}


def make_note(alias, title=None, tags=(), links=()):
    note_id = IDS[alias]
    return Note(
        id=note_id,
        title=title or f"Note {alias}",
        created=NOW,
        modified=NOW,
        tags=tags,
        links=links,
        body="",
    )


@scenario("features/graph.feature", "Add and retrieve a note")
def test_add_and_get():
    pass


@scenario("features/graph.feature", "Get returns nothing for unknown ID")
def test_get_unknown():
    pass


@scenario("features/graph.feature", "Outgoing links")
def test_outgoing():
    pass


@scenario("features/graph.feature", "Incoming links")
def test_incoming():
    pass


@scenario("features/graph.feature", "Neighbors returns both directions")
def test_neighbors():
    pass


@scenario("features/graph.feature", "Filter by tag")
def test_filter_by_tag():
    pass


@given(
    parsers.parse('a graph with a note "{note_id}" titled "{title}"'),
    target_fixture="graph",
)
def graph_with_one_note(note_id, title):
    g = Graph()
    note = Note(
        id=note_id,
        title=title,
        created=NOW,
        modified=NOW,
        tags=(),
        links=(),
        body="",
    )
    g.add(note)
    return g


@given("an empty graph", target_fixture="graph")
def empty_graph():
    return Graph()


@given('a graph where "A" links to "B" and "C"', target_fixture="graph")
def graph_a_links_b_c():
    g = Graph()
    g.add(
        make_note(
            "A",
            links=(
                Link(target_id=IDS["B"], link_type="linksTo"),
                Link(target_id=IDS["C"], link_type="linksTo"),
            ),
        )
    )
    g.add(make_note("B"))
    g.add(make_note("C"))
    return g


@given(
    'a graph where "A" links to "B" and "C" links to "A"',
    target_fixture="graph",
)
def graph_a_to_b_and_c_to_a():
    g = Graph()
    g.add(make_note("A", links=(Link(target_id=IDS["B"], link_type="linksTo"),)))
    g.add(make_note("B"))
    g.add(make_note("C", links=(Link(target_id=IDS["A"], link_type="linksTo"),)))
    return g


@given(
    'a graph with notes tagged "rdf" and "python"',
    target_fixture="graph",
)
def graph_with_tagged_notes():
    g = Graph()
    g.add(make_note("A", tags=(Tag(name="rdf"),)))
    g.add(make_note("B", tags=(Tag(name="python"),)))
    g.add(make_note("C", tags=(Tag(name="rdf"), Tag(name="python"))))
    return g


@when(parsers.parse('I get note "{note_id}"'), target_fixture="result")
def get_note(graph, note_id):
    return graph.get(note_id)


@when(parsers.parse('I ask for outgoing from "{alias}"'), target_fixture="result")
def get_outgoing(graph, alias):
    return graph.outgoing(IDS[alias])


@when(parsers.parse('I ask for incoming to "{alias}"'), target_fixture="result")
def get_incoming(graph, alias):
    return graph.incoming(IDS[alias])


@when(parsers.parse('I ask for neighbors of "{alias}"'), target_fixture="result")
def get_neighbors(graph, alias):
    return graph.neighbors(IDS[alias])


@when(parsers.parse('I filter by tag "{tag}"'), target_fixture="result")
def filter_tag(graph, tag):
    return graph.filter_by_tag(tag)


@then(parsers.parse('the result is "{expected}"'))
def check_result_title(result, expected):
    assert isinstance(result, Note)
    assert result.title == expected


@then("the result is empty")
def check_result_none(result):
    assert result is None


@then(parsers.parse('the result contains "{a}" and "{b}"'))
def check_result_contains(result, a, b):
    ids = {n.id for n in result}
    assert IDS[a] in ids
    assert IDS[b] in ids


@then(parsers.parse('the result contains "{alias}"'))
def check_result_contains_one(result, alias):
    ids = {n.id for n in result}
    assert IDS[alias] in ids


@then('only notes tagged "rdf" are returned')
def check_rdf_filter(result):
    assert len(result) == 2
    for note in result:
        assert any(t.name == "rdf" for t in note.tags)
