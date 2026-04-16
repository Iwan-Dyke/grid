from dataclasses import dataclass

from grid.note_modeling.identifiers import validate_note_id


@dataclass(frozen=True)
class Link:
    target_id: str
    link_type: str
    label: str | None = None

    def __post_init__(self):
        validate_note_id(self.target_id)
        stripped = self.link_type.strip()
        if not stripped:
            raise ValueError("link_type cannot be empty")
        object.__setattr__(self, "link_type", stripped)
