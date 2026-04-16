import re
from datetime import UTC, datetime

NOTE_ID_PATTERN = re.compile(r"^\d{14}$")


def validate_note_id(note_id: str) -> None:
    if not note_id or not NOTE_ID_PATTERN.match(note_id):
        raise ValueError("Note ID must be a 14-digit timestamp")


def generate_note_id() -> str:
    return datetime.now(UTC).strftime("%Y%m%d%H%M%S")
