from pytest_bdd import scenario, given, when, then, parsers

from grid import service
from grid.note_modeling import Graph, Tag
from grid.vault_parsing import MarkdownFileRepository

from tests.service.conftest import make_note


@scenario("features/service.feature", "Loading the vault reconciles body links into frontmatter")
def test_load_reconciles():
    pass


@scenario("features/service.feature", "Creating a note persists it to the vault")
def test_create_persists():
    pass


@scenario("features/service.feature", "Adding a link appends to body and updates frontmatter")
def test_add_link_updates_both():
    pass


@scenario("features/service.feature", "Syncing the vault reconciles every note")
def test_sync_reconciles_all():
    pass


@scenario("features/service.feature", "Search finds notes by title")
def test_search_finds_by_title():
    pass


@scenario("features/service.feature", "List filters by tag and type")
def test_list_filters():
    pass


@scenario("features/service.feature", "Export produces RDF turtle")
def test_export_turtle():
    pass


@given(
    parsers.parse('a vault with a note whose body contains "{body}"'),
    target_fixture="repo",
)
def vault_with_body(tmp_path, body):
    repo = MarkdownFileRepository(tmp_path)
    repo.save(make_note(body=body))
    return repo


@given("a vault with a note whose body is empty", target_fixture="repo")
def vault_with_empty_body(tmp_path):
    repo = MarkdownFileRepository(tmp_path)
    repo.save(make_note(body=""))
    return repo


@given("an empty vault", target_fixture="repo")
def empty_vault(tmp_path):
    return MarkdownFileRepository(tmp_path)


@given(
    parsers.parse('a graph with a note titled "{title}"'),
    target_fixture="graph",
)
def graph_with_titled_note(title):
    g = Graph()
    g.add(make_note(title=title))
    return g


@given(
    "a graph with notes with different tags and types",
    target_fixture="graph",
)
def graph_with_mixed_notes():
    g = Graph()
    g.add(make_note(
        id="20260409221400", tags=(Tag(name="rdf"),), note_type="reference"
    ))
    g.add(make_note(
        id="20260409221401", title="A",
        tags=(Tag(name="python"),), note_type="reference",
    ))
    g.add(make_note(
        id="20260409221402", title="B",
        tags=(Tag(name="rdf"),), note_type="note",
    ))
    return g


@given("a graph with a note", target_fixture="graph")
def graph_with_note():
    g = Graph()
    g.add(make_note())
    return g


@when("the vault is loaded", target_fixture="graph")
def load_vault(repo):
    return service.load_graph(repo)


@when(
    parsers.parse('a note is created with title "{title}"'),
    target_fixture="created",
)
def create_with_title(repo, title):
    return service.create_note(repo, title, "note", [])


@when(
    parsers.parse('a "{link_type}" link to "{target}" is added'),
    target_fixture="updated",
)
def add_typed_link(repo, link_type, target):
    return service.add_link(repo, "20260409221400", target, link_type)


@when("the vault is synced", target_fixture="synced")
def sync_vault(repo):
    return service.sync_all(repo)


@when(
    parsers.parse('the graph is searched for "{query}"'),
    target_fixture="results",
)
def search_graph(graph, query):
    return service.search(graph, query)


@when(
    parsers.parse('listing notes with tag "{tag}" and type "{note_type}"'),
    target_fixture="results",
)
def list_graph(graph, tag, note_type):
    return service.list_notes(graph, tag=tag, note_type=note_type)


@when("the graph is exported as turtle", target_fixture="output")
def export_turtle(graph):
    return service.export_rdf(graph, format="turtle")


@then(parsers.parse("the note in the graph has {count:d} link"))
def graph_note_link_count(graph, count):
    assert len(graph.get("20260409221400").links) == count


@then("the reconciled note is written to disk")
def reconciled_on_disk(repo):
    reloaded = MarkdownFileRepository(repo._vault_path).load("20260409221400")
    assert len(reloaded.links) == 1


@then("the note exists in the vault")
def created_exists(repo, created):
    assert repo.exists(created.id)


@then("the note has a 14-digit ID")
def id_is_14_digits(created):
    assert len(created.id) == 14
    assert created.id.isdigit()


@then(parsers.parse('the body contains "{fragment}"'))
def body_contains(updated, fragment):
    assert fragment in updated.body


@then(parsers.parse('the frontmatter links contain "{target}"'))
def links_contain(updated, target):
    assert any(link.target_id == target for link in updated.links)


@then("every returned note is reconciled")
def every_note_reconciled(synced):
    for note in synced:
        assert note.links == () or all(
            link.target_id.isdigit() for link in note.links
        )


@then("the matching note is returned")
def matching_note_returned(results):
    assert len(results) >= 1
    assert results[0].title == "Python Basics"


@then("only the matching note is returned")
def only_match_returned(results):
    assert len(results) == 1
    assert results[0].id == "20260409221400"


@then("the output contains the note ID")
def output_contains_id(output):
    assert "20260409221400" in output
