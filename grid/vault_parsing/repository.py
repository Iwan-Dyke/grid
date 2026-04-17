from pathlib import Path

from grid.note_modeling import Note
from grid.vault_parsing.filename import generate_filename
from grid.vault_parsing.parser import parse_note, serialize_note
from grid.vault_parsing.errors import NoteNotFoundError, NoteParseError


class MarkdownFileRepository:
    def __init__(self, vault_path: Path):
        self._vault_path = vault_path
        self._index: dict[str, Path] = {}

    def load(self, note_id: str) -> Note:
        path = self._resolve(note_id)
        return parse_note(path)

    def load_all(self) -> list[Note]:
        self._index.clear()
        notes = []
        for path in sorted(self._vault_path.glob("*.md")):
            note = parse_note(path)
            if note.id in self._index:
                raise NoteParseError(f"Duplicate note ID {note.id} in {path.name}")
            self._index[note.id] = path
            notes.append(note)
        return notes

    def load_raw(self, note_id: str) -> str:
        path = self._resolve(note_id)
        return path.read_text()

    def save(self, note: Note) -> None:
        filename = generate_filename(note.id, note.title)
        path = self._vault_path / filename

        old_path = self._index.get(note.id)
        if old_path and old_path != path and old_path.exists():
            old_path.unlink()

        path.write_text(serialize_note(note))
        self._index[note.id] = path

    def delete(self, note_id: str) -> None:
        path = self._resolve(note_id)
        path.unlink()
        del self._index[note_id]

    def exists(self, note_id: str) -> bool:
        if note_id in self._index:
            return True
        return any(self._vault_path.glob(f"{note_id}-*.md"))

    def _resolve(self, note_id: str) -> Path:
        if note_id in self._index:
            return self._index[note_id]
        for path in self._vault_path.glob(f"{note_id}-*.md"):
            self._index[note_id] = path
            return path
        raise NoteNotFoundError(f"Note {note_id} not found")
