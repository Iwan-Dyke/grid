import re
from dataclasses import dataclass

from grid.note_modeling.identifiers import validate_note_id

LINK_TYPE_PATTERN = re.compile(r"^\w+$")


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
        if not LINK_TYPE_PATTERN.match(stripped):
            raise ValueError(
                "link_type must contain only letters, digits, or underscores"
            )
        object.__setattr__(self, "link_type", stripped)
