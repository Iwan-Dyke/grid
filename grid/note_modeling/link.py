import re
from dataclasses import dataclass

NOTE_ID_PATTERN = re.compile(r"^\d{14}$")


@dataclass(frozen=True)
class Link:
    target_id: str
    link_type: str
    label: str | None = None

    def __post_init__(self):
        if not self.target_id or not NOTE_ID_PATTERN.match(self.target_id):
            raise ValueError("target_id must be a 14-digit timestamp")
        if not self.link_type:
            raise ValueError("link_type cannot be empty")
