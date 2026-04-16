from dataclasses import dataclass
from datetime import datetime

from grid.note_modeling.identifiers import validate_note_id
from grid.note_modeling.tag import Tag
from grid.note_modeling.link import Link


@dataclass(frozen=True)
class Note:
    id: str
    title: str
    created: datetime
    modified: datetime
    tags: tuple[Tag, ...]
    links: tuple[Link, ...]
    body: str
    note_type: str = "note"

    def __post_init__(self):
        validate_note_id(self.id)
        stripped_title = self.title.strip()
        if not stripped_title:
            raise ValueError("title cannot be empty")
        object.__setattr__(self, "title", stripped_title)
        stripped_type = self.note_type.strip()
        if not stripped_type:
            raise ValueError("note_type cannot be empty")
        object.__setattr__(self, "note_type", stripped_type)
        if self.modified < self.created:
            raise ValueError("modified cannot be before created")
