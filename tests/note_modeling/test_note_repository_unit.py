from datetime import datetime, UTC

from grid.note_modeling.ports import NoteRepository
from grid.note_modeling import Note


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


class FakeNoteRepository:
    def __init__(self):
        self._notes = {}

    def load(self, note_id: str) -> Note:
        return self._notes[note_id]

    def load_all(self) -> list[Note]:
        return list(self._notes.values())

    def load_raw(self, note_id: str) -> str:
        return ""

    def save(self, note: Note) -> None:
        self._notes[note.id] = note

    def delete(self, note_id: str) -> None:
        del self._notes[note_id]

    def exists(self, note_id: str) -> bool:
        return note_id in self._notes


class TestNoteRepositoryProtocol:
    def test_fake_satisfies_protocol(self):
        assert isinstance(FakeNoteRepository(), NoteRepository)

    def test_save_and_load(self):
        repo = FakeNoteRepository()
        note = make_note()
        repo.save(note)
        assert repo.load(note.id) == note

    def test_load_all(self):
        repo = FakeNoteRepository()
        repo.save(make_note(id="20260409221400"))
        repo.save(make_note(id="20260409221401", title="Second"))
        assert len(repo.load_all()) == 2

    def test_exists(self):
        repo = FakeNoteRepository()
        repo.save(make_note())
        assert repo.exists("20260409221400")
        assert not repo.exists("99999999999999")

    def test_delete(self):
        repo = FakeNoteRepository()
        repo.save(make_note())
        repo.delete("20260409221400")
        assert not repo.exists("20260409221400")
