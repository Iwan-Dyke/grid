import pytest
from datetime import datetime, UTC

from grid.note_modeling.graph import Graph
from grid.note_modeling.note import Note
from grid.note_modeling.tag import Tag
from grid.note_modeling.link import Link


NOW = datetime(2026, 4, 9, 22, 14, 0, tzinfo=UTC)

IDS = {
    "A": "20260409221400",
    "B": "20260409221401",
    "C": "20260409221402",
    "D": "20260409221403",
}


def make_note(alias, tags=(), links=()):
    return Note(
        id=IDS[alias],
        title=f"Note {alias}",
        created=NOW,
        modified=NOW,
        tags=tags,
        links=links,
        body="",
    )


class TestGraphAdd:
    def test_add_and_get(self):
        g = Graph()
        note = make_note("A")
        g.add(note)
        assert g.get(IDS["A"]) == note

    def test_get_unknown_returns_none(self):
        g = Graph()
        assert g.get("99999999999999") is None

    def test_all_notes(self):
        g = Graph()
        g.add(make_note("A"))
        g.add(make_note("B"))
        assert len(g.all_notes()) == 2

    def test_add_duplicate_id_raises(self):
        g = Graph()
        g.add(make_note("A"))
        with pytest.raises(ValueError):
            g.add(make_note("A"))


class TestGraphTraversalUnknownId:
    def test_outgoing_unknown_id(self):
        g = Graph()
        assert g.outgoing("99999999999999") == []

    def test_incoming_unknown_id(self):
        g = Graph()
        assert g.incoming("99999999999999") == []

    def test_neighbors_unknown_id(self):
        g = Graph()
        assert g.neighbors("99999999999999") == []


class TestGraphOutgoing:
    def test_returns_linked_notes(self):
        g = Graph()
        g.add(make_note("A", links=(
            Link(target_id=IDS["B"], link_type="linksTo"),
        )))
        g.add(make_note("B"))
        result = g.outgoing(IDS["A"])
        assert len(result) == 1
        assert result[0].id == IDS["B"]

    def test_skips_missing_targets(self):
        g = Graph()
        g.add(make_note("A", links=(
            Link(target_id=IDS["B"], link_type="linksTo"),
        )))
        result = g.outgoing(IDS["A"])
        assert result == []

    def test_empty_when_no_links(self):
        g = Graph()
        g.add(make_note("A"))
        assert g.outgoing(IDS["A"]) == []


class TestGraphIncoming:
    def test_returns_notes_linking_here(self):
        g = Graph()
        g.add(make_note("A", links=(
            Link(target_id=IDS["B"], link_type="linksTo"),
        )))
        g.add(make_note("B"))
        result = g.incoming(IDS["B"])
        assert len(result) == 1
        assert result[0].id == IDS["A"]

    def test_empty_when_nothing_links_here(self):
        g = Graph()
        g.add(make_note("A"))
        g.add(make_note("B"))
        assert g.incoming(IDS["A"]) == []


class TestGraphNeighbors:
    def test_union_of_outgoing_and_incoming(self):
        g = Graph()
        g.add(make_note("A", links=(
            Link(target_id=IDS["B"], link_type="linksTo"),
        )))
        g.add(make_note("B"))
        g.add(make_note("C", links=(
            Link(target_id=IDS["A"], link_type="linksTo"),
        )))
        result = g.neighbors(IDS["A"])
        ids = {n.id for n in result}
        assert ids == {IDS["B"], IDS["C"]}

    def test_no_duplicates(self):
        g = Graph()
        g.add(make_note("A", links=(
            Link(target_id=IDS["B"], link_type="linksTo"),
        )))
        g.add(make_note("B", links=(
            Link(target_id=IDS["A"], link_type="related"),
        )))
        result = g.neighbors(IDS["A"])
        ids = [n.id for n in result]
        assert len(ids) == len(set(ids))


class TestGraphFilterByTag:
    def test_returns_matching_notes(self):
        g = Graph()
        g.add(make_note("A", tags=(Tag(name="rdf"),)))
        g.add(make_note("B", tags=(Tag(name="python"),)))
        result = g.filter_by_tag("rdf")
        assert len(result) == 1
        assert result[0].id == IDS["A"]

    def test_returns_empty_when_no_match(self):
        g = Graph()
        g.add(make_note("A", tags=(Tag(name="rdf"),)))
        assert g.filter_by_tag("go") == []

    def test_matches_notes_with_multiple_tags(self):
        g = Graph()
        g.add(make_note("A", tags=(Tag(name="rdf"), Tag(name="python"))))
        result = g.filter_by_tag("python")
        assert len(result) == 1
