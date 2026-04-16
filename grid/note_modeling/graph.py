from grid.note_modeling.note import Note


class Graph:
    def __init__(self):
        self._notes: dict[str, Note] = {}

    def add(self, note: Note) -> None:
        if note.id in self._notes:
            raise ValueError(f"Duplicate note ID: {note.id}")
        self._notes[note.id] = note

    def get(self, note_id: str) -> Note | None:
        return self._notes.get(note_id)

    def all_notes(self) -> list[Note]:
        return list(self._notes.values())

    def outgoing(self, note_id: str) -> list[Note]:
        note = self._notes.get(note_id)
        if note is None:
            return []
        return [
            self._notes[link.target_id]
            for link in note.links
            if link.target_id in self._notes
        ]

    def incoming(self, note_id: str) -> list[Note]:
        return [
            note
            for note in self._notes.values()
            if any(link.target_id == note_id for link in note.links)
        ]

    def neighbors(self, note_id: str) -> list[Note]:
        seen = set()
        result = []
        for note in self.outgoing(note_id) + self.incoming(note_id):
            if note.id not in seen:
                seen.add(note.id)
                result.append(note)
        return result

    def filter_by_tag(self, tag: str) -> list[Note]:
        return [
            note
            for note in self._notes.values()
            if any(t.name == tag for t in note.tags)
        ]
