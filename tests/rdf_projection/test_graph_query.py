from pytest_bdd import scenario, given, when, then, parsers

from grid.rdf_projection import RDFlibGraphQuery

from tests.rdf_projection.conftest import make_note


@scenario("features/graph_query.feature", "SPARQL query with built-in prefix finds notes")
def test_sparql_prefix_auto_injected():
    pass


@scenario("features/graph_query.feature", "Serializing to Turtle includes the note identifier")
def test_serialize_turtle():
    pass


@scenario("features/graph_query.feature", "Custom grid URI is used in the serialized output")
def test_custom_grid_uri():
    pass


@scenario("features/graph_query.feature", "Extra namespaces are registered as prefixes")
def test_extra_namespaces():
    pass


@given(
    parsers.parse("a graph query built from {count:d} notes"),
    target_fixture="query",
)
def query_from_n_notes(count):
    q = RDFlibGraphQuery()
    ids = [f"2026040922140{i}" for i in range(count)]
    q.build([make_note(id=note_id, title=f"Note {note_id}") for note_id in ids])
    return q


@given(
    parsers.parse('a graph query built from 1 note with id "{note_id}"'),
    target_fixture="query",
)
def query_from_note_with_id(note_id):
    q = RDFlibGraphQuery()
    q.build([make_note(id=note_id)])
    return q


@given(
    parsers.parse(
        'a graph query using grid URI "{grid_uri}" built from 1 note'
    ),
    target_fixture="query",
)
def query_custom_grid_uri(grid_uri):
    q = RDFlibGraphQuery(grid_uri=grid_uri)
    q.build([make_note()])
    return q


@given(
    parsers.parse(
        'a graph query with extra namespace "{prefix}" bound to "{uri}"'
    ),
    target_fixture="query",
)
def query_with_extra_namespace(prefix, uri):
    return RDFlibGraphQuery(extra_namespaces={prefix: uri})


@when(
    parsers.parse('I run the SPARQL query "{sparql}"'),
    target_fixture="results",
)
def run_sparql(query, sparql):
    return query.query(sparql)


@when(
    parsers.parse('I serialize the graph to "{fmt}"'),
    target_fixture="output",
)
def serialize_graph(query, fmt):
    return query.serialize(format=fmt)


@then(parsers.parse("{count:d} results are returned"))
def check_result_count(results, count):
    assert len(results) == count


@then(parsers.parse('the output contains "{needle}"'))
def check_output_contains(output, needle):
    assert needle in output


@then(parsers.parse('the prefixes include "{prefix}"'))
def check_prefix_present(query, prefix):
    assert prefix in query.prefixes
