import pytest
from datetime import datetime, UTC

from grid import service
from grid.note_modeling import Graph, Link, Tag
from grid.vault_parsing import MarkdownFileRepository
from grid.vault_parsing.errors import NoteNotFoundError

from tests.service.conftest import make_note


def _graph(*notes):
    g = Graph()
    for n in notes:
        g.add(n)
    return g


class TestLoadGraph:
    def test_returns_graph_with_all_notes(self, tmp_path):
        repo = MarkdownFileRepository(tmp_path)
        repo.save(make_note(id="20260409221400", title="First"))
        repo.save(make_note(id="20260409221401", title="Second"))
        graph = service.load_graph(repo)
        assert len(graph.all_notes()) == 2

    def test_reconciles_body_links_into_frontmatter(self, tmp_path):
        repo = MarkdownFileRepository(tmp_path)
        repo.save(make_note(body="See [[20260101120000]]"))
        graph = service.load_graph(repo)
        note = graph.get("20260409221400")
        assert len(note.links) == 1
        assert note.links[0].target_id == "20260101120000"

    def test_persists_reconciled_note_to_disk(self, tmp_path):
        repo = MarkdownFileRepository(tmp_path)
        repo.save(make_note(body="See [[20260101120000]]"))
        service.load_graph(repo)
        reloaded = MarkdownFileRepository(tmp_path).load("20260409221400")
        assert len(reloaded.links) == 1

    def test_does_not_rewrite_unchanged_note(self, tmp_path):
        repo = MarkdownFileRepository(tmp_path)
        repo.save(make_note(body="plain text"))
        path = next(tmp_path.glob("*.md"))
        mtime_before = path.stat().st_mtime_ns
        service.load_graph(repo)
        assert path.stat().st_mtime_ns == mtime_before

    def test_empty_vault_returns_empty_graph(self, tmp_path):
        repo = MarkdownFileRepository(tmp_path)
        graph = service.load_graph(repo)
        assert graph.all_notes() == []


class TestLoadNote:
    def test_returns_single_note(self, tmp_path):
        repo = MarkdownFileRepository(tmp_path)
        repo.save(make_note())
        loaded = service.load_note(repo, "20260409221400")
        assert loaded.id == "20260409221400"

    def test_reconciles_on_load(self, tmp_path):
        repo = MarkdownFileRepository(tmp_path)
        repo.save(make_note(body="[[related::20260101120000]]"))
        loaded = service.load_note(repo, "20260409221400")
        assert loaded.links[0].link_type == "related"

    def test_persists_reconciled_version(self, tmp_path):
        repo = MarkdownFileRepository(tmp_path)
        repo.save(make_note(body="[[20260101120000]]"))
        service.load_note(repo, "20260409221400")
        reloaded = MarkdownFileRepository(tmp_path).load("20260409221400")
        assert len(reloaded.links) == 1

    def test_raises_for_missing_id(self, tmp_path):
        repo = MarkdownFileRepository(tmp_path)
        with pytest.raises(NoteNotFoundError):
            service.load_note(repo, "99999999999999")


class TestGetRaw:
    def test_returns_file_text(self, tmp_path):
        repo = MarkdownFileRepository(tmp_path)
        repo.save(make_note(body="raw body"))
        raw = service.get_raw(repo, "20260409221400")
        assert "raw body" in raw

    def test_raises_for_missing_id(self, tmp_path):
        repo = MarkdownFileRepository(tmp_path)
        with pytest.raises(NoteNotFoundError):
            service.get_raw(repo, "99999999999999")


class TestCreateNote:
    def test_persists_to_disk(self, tmp_path):
        repo = MarkdownFileRepository(tmp_path)
        note = service.create_note(repo, "Hello", "note", ["rdf"])
        assert repo.exists(note.id)

    def test_generates_id(self, tmp_path):
        repo = MarkdownFileRepository(tmp_path)
        note = service.create_note(repo, "Hello", "note", [])
        assert len(note.id) == 14
        assert note.id.isdigit()

    def test_sets_tags(self, tmp_path):
        repo = MarkdownFileRepository(tmp_path)
        note = service.create_note(repo, "Hello", "note", ["rdf", "linked-data"])
        assert note.tags == (Tag(name="rdf"), Tag(name="linked-data"))

    def test_preserves_note_type(self, tmp_path):
        repo = MarkdownFileRepository(tmp_path)
        note = service.create_note(repo, "Hello", "reference", [])
        assert note.note_type == "reference"

    def test_created_equals_modified(self, tmp_path):
        repo = MarkdownFileRepository(tmp_path)
        note = service.create_note(repo, "Hello", "note", [])
        assert note.created == note.modified

    def test_body_is_empty(self, tmp_path):
        repo = MarkdownFileRepository(tmp_path)
        note = service.create_note(repo, "Hello", "note", [])
        assert note.body == ""

    def test_invalid_tag_raises(self, tmp_path):
        repo = MarkdownFileRepository(tmp_path)
        with pytest.raises(ValueError):
            service.create_note(repo, "Hello", "note", ["Invalid Tag!"])


class TestAddLink:
    def test_default_type_inserts_bare_wiki_link(self, tmp_path):
        repo = MarkdownFileRepository(tmp_path)
        repo.save(make_note(body="some content"))
        updated = service.add_link(repo, "20260409221400", "20260101120000", "linksTo")
        assert "[[20260101120000]]" in updated.body

    def test_typed_link_inserts_typed_syntax(self, tmp_path):
        repo = MarkdownFileRepository(tmp_path)
        repo.save(make_note(body="some content"))
        updated = service.add_link(repo, "20260409221400", "20260101120000", "related")
        assert "[[related::20260101120000]]" in updated.body

    def test_labelled_link_inserts_full_syntax(self, tmp_path):
        repo = MarkdownFileRepository(tmp_path)
        repo.save(make_note(body="content"))
        updated = service.add_link(
            repo, "20260409221400", "20260101120000", "related", "see this"
        )
        assert "[[related::20260101120000|see this]]" in updated.body

    def test_link_syncs_into_frontmatter(self, tmp_path):
        repo = MarkdownFileRepository(tmp_path)
        repo.save(make_note(body=""))
        updated = service.add_link(repo, "20260409221400", "20260101120000", "related")
        assert Link(target_id="20260101120000", link_type="related") in updated.links

    def test_persists_to_disk(self, tmp_path):
        repo = MarkdownFileRepository(tmp_path)
        repo.save(make_note(body=""))
        service.add_link(repo, "20260409221400", "20260101120000", "linksTo")
        reloaded = MarkdownFileRepository(tmp_path).load("20260409221400")
        assert len(reloaded.links) == 1

    def test_appends_to_existing_body_with_separator(self, tmp_path):
        repo = MarkdownFileRepository(tmp_path)
        repo.save(make_note(body="existing"))
        updated = service.add_link(repo, "20260409221400", "20260101120000", "linksTo")
        assert updated.body.startswith("existing\n")

    def test_empty_body_no_leading_newline(self, tmp_path):
        repo = MarkdownFileRepository(tmp_path)
        repo.save(make_note(body=""))
        updated = service.add_link(repo, "20260409221400", "20260101120000", "linksTo")
        assert updated.body == "[[20260101120000]]\n"

    def test_body_ending_in_newline_no_double(self, tmp_path):
        repo = MarkdownFileRepository(tmp_path)
        repo.save(make_note(body="existing\n"))
        updated = service.add_link(repo, "20260409221400", "20260101120000", "linksTo")
        assert "existing\n\n[[" not in updated.body
        assert updated.body == "existing\n[[20260101120000]]\n"

    def test_bumps_modified(self, tmp_path, now, later):
        repo = MarkdownFileRepository(tmp_path)
        repo.save(make_note(body="", modified=now))
        updated = service.add_link(repo, "20260409221400", "20260101120000", "linksTo")
        assert updated.modified > now

    def test_raises_for_missing_source(self, tmp_path):
        repo = MarkdownFileRepository(tmp_path)
        with pytest.raises(NoteNotFoundError):
            service.add_link(repo, "99999999999999", "20260101120000", "linksTo")


class TestSyncNote:
    def test_returns_reconciled_note(self, tmp_path):
        repo = MarkdownFileRepository(tmp_path)
        repo.save(make_note(body="[[20260101120000]]"))
        result = service.sync_note(repo, "20260409221400")
        assert len(result.links) == 1

    def test_persists_changes(self, tmp_path):
        repo = MarkdownFileRepository(tmp_path)
        repo.save(make_note(body="[[20260101120000]]"))
        service.sync_note(repo, "20260409221400")
        reloaded = MarkdownFileRepository(tmp_path).load("20260409221400")
        assert len(reloaded.links) == 1

    def test_noop_when_nothing_to_sync(self, tmp_path):
        repo = MarkdownFileRepository(tmp_path)
        repo.save(make_note(body="plain text"))
        path = next(tmp_path.glob("*.md"))
        mtime_before = path.stat().st_mtime_ns
        result = service.sync_note(repo, "20260409221400")
        assert result.links == ()
        assert path.stat().st_mtime_ns == mtime_before


class TestSyncAll:
    def test_reconciles_every_note(self, tmp_path):
        repo = MarkdownFileRepository(tmp_path)
        repo.save(make_note(id="20260409221400", body="[[20260101120000]]"))
        repo.save(make_note(id="20260409221401", title="Other", body=""))
        notes = service.sync_all(repo)
        assert len(notes) == 2

    def test_empty_vault(self, tmp_path):
        repo = MarkdownFileRepository(tmp_path)
        assert service.sync_all(repo) == []

    def test_mix_of_changed_and_unchanged(self, tmp_path):
        repo = MarkdownFileRepository(tmp_path)
        repo.save(make_note(id="20260409221400", body="[[20260101120000]]"))
        repo.save(make_note(id="20260409221401", title="Other", body="no links"))
        notes = service.sync_all(repo)
        changed = next(n for n in notes if n.id == "20260409221400")
        unchanged = next(n for n in notes if n.id == "20260409221401")
        assert len(changed.links) == 1
        assert unchanged.links == ()


class TestListNotes:
    def test_sorts_by_modified_descending(self):
        newer = make_note(
            id="20260409221401",
            title="Newer",
            modified=datetime(2026, 4, 10, tzinfo=UTC),
        )
        older = make_note(id="20260409221400", title="Older")
        result = service.list_notes(_graph(older, newer))
        assert [n.id for n in result] == [newer.id, older.id]

    def test_filters_by_tag(self):
        tagged = make_note(id="20260409221400", tags=(Tag(name="rdf"),))
        untagged = make_note(id="20260409221401", title="Other")
        result = service.list_notes(_graph(tagged, untagged), tag="rdf")
        assert [n.id for n in result] == [tagged.id]

    def test_filters_by_type(self):
        note = make_note(id="20260409221400", note_type="note")
        ref = make_note(id="20260409221401", title="Ref", note_type="reference")
        result = service.list_notes(_graph(note, ref), note_type="reference")
        assert [n.id for n in result] == [ref.id]

    def test_combines_tag_and_type_filters_with_and_logic(self):
        match = make_note(
            id="20260409221400", tags=(Tag(name="rdf"),), note_type="reference"
        )
        wrong_tag = make_note(
            id="20260409221401",
            title="A",
            tags=(Tag(name="python"),),
            note_type="reference",
        )
        wrong_type = make_note(
            id="20260409221402",
            title="B",
            tags=(Tag(name="rdf"),),
            note_type="note",
        )
        result = service.list_notes(
            _graph(match, wrong_tag, wrong_type),
            tag="rdf",
            note_type="reference",
        )
        assert [n.id for n in result] == [match.id]

    def test_empty_graph_returns_empty_list(self):
        assert service.list_notes(Graph()) == []

    def test_filters_with_no_matches_returns_empty(self):
        note = make_note(tags=(Tag(name="rdf"),))
        assert service.list_notes(_graph(note), tag="nonexistent") == []


class TestSearch:
    def test_matches_on_title(self):
        match = make_note(id="20260409221400", title="Python Basics")
        other = make_note(id="20260409221401", title="Rust Guide")
        result = service.search(_graph(match, other), "python")
        assert match in result
        assert other not in result

    def test_matches_on_body(self):
        match = make_note(
            id="20260409221400",
            title="Misc",
            body="We write a lot of python here",
        )
        other = make_note(id="20260409221401", title="Other", body="nothing")
        result = service.search(_graph(match, other), "python")
        assert match in result
        assert other not in result

    def test_ranks_higher_scores_first(self):
        strong = make_note(id="20260409221400", title="Python Basics")
        weak = make_note(
            id="20260409221401",
            title="Misc",
            body="mentions python once",
        )
        result = service.search(_graph(weak, strong), "python basics")
        assert result[0] == strong

    def test_case_insensitive(self):
        note = make_note(title="Python Basics")
        result = service.search(_graph(note), "PYTHON")
        assert note in result

    def test_empty_query_returns_empty(self):
        note = make_note(title="Python")
        assert service.search(_graph(note), "") == []
        assert service.search(_graph(note), "   ") == []

    def test_no_match_returns_empty(self):
        note = make_note(title="Rust Guide", body="about rust")
        assert service.search(_graph(note), "javascript") == []

    def test_trims_query_whitespace(self):
        note = make_note(title="Python Basics")
        result = service.search(_graph(note), "  python  ")
        assert note in result


class TestExportRdf:
    def test_turtle_contains_note_identifier(self):
        note = make_note(id="20260409221400", title="My Note")
        output = service.export_rdf(_graph(note), format="turtle")
        assert "20260409221400" in output
        assert "My Note" in output

    def test_ntriples_format(self):
        note = make_note()
        output = service.export_rdf(_graph(note), format="nt")
        assert output.strip().endswith(".")

    def test_empty_graph_produces_valid_output(self):
        output = service.export_rdf(Graph(), format="turtle")
        assert isinstance(output, str)

    def test_renders_links(self):
        source = make_note(
            id="20260409221400",
            links=(Link(target_id="20260409221401", link_type="related"),),
        )
        target = make_note(id="20260409221401", title="Other")
        output = service.export_rdf(_graph(source, target), format="turtle")
        assert "related" in output


class TestQuerySparql:
    def test_selects_all_notes(self):
        note = make_note(id="20260409221400", title="My Note")
        rows = service.query_sparql(
            _graph(note),
            "SELECT ?s WHERE { ?s a grid:Note }",
        )
        assert len(rows) == 1
        assert "20260409221400" in rows[0]["s"]

    def test_returns_empty_list_for_no_matches(self):
        rows = service.query_sparql(
            Graph(),
            "SELECT ?s WHERE { ?s a grid:Note }",
        )
        assert rows == []

    def test_filters_by_tag(self):
        tagged = make_note(id="20260409221400", tags=(Tag(name="rdf"),))
        untagged = make_note(id="20260409221401", title="Other")
        rows = service.query_sparql(
            _graph(tagged, untagged),
            "SELECT ?s WHERE { ?s dcterms:subject ?tag }",
        )
        ids = {row["s"] for row in rows}
        assert any("20260409221400" in s for s in ids)
        assert not any("20260409221401" in s for s in ids)
