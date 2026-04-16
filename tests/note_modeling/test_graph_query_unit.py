from datetime import datetime, UTC

from grid.note_modeling.ports import GraphQuery
from grid.note_modeling import Note, Triple


NOW = datetime(2026, 4, 9, 22, 14, 0, tzinfo=UTC)


def make_note(**overrides):
    defaults = {
        "id": "20260409221400",
        "title": "Test Note",
        "created": NOW,
        "modified": NOW,
        "tags": (),
        "links": (),
        "body": "",
    }
    defaults.update(overrides)
    return Note(**defaults)


class FakeGraphQuery:
    def build(self, notes: list[Note]) -> list[Triple]:
        return [
            Triple(
                subject=f"grid:{n.id}",
                predicate="a",
                object="grid:Note",
            )
            for n in notes
        ]

    def query(self, sparql: str) -> list[dict]:
        return [{"result": "fake"}]


class TestGraphQueryProtocol:
    def test_fake_satisfies_protocol(self):
        assert isinstance(FakeGraphQuery(), GraphQuery)

    def test_build_returns_triples(self):
        gq = FakeGraphQuery()
        notes = [make_note()]
        result = gq.build(notes)
        assert len(result) == 1
        assert isinstance(result[0], Triple)

    def test_query_returns_dicts(self):
        gq = FakeGraphQuery()
        result = gq.query("SELECT ?s WHERE { ?s ?p ?o }")
        assert isinstance(result, list)
        assert isinstance(result[0], dict)
