from dataclasses import dataclass

from grid.note_modeling.identifiers import validate_note_id


@dataclass(frozen=True)
class Link:
    target_id: str
    link_type: str
    label: str | None = None

    def __post_init__(self):
        validate_note_id(self.target_id)
        if not self.link_type:
            raise ValueError("link_type cannot be empty")
