import re
from enum import Enum
from pathlib import Path

_GRID_NOTE_PATTERN = re.compile(r"^\d{14}-.*\.md$")


class DirState(Enum):
    ABSENT = "absent"
    EMPTY_OR_VAULT = "empty_or_vault"
    HAS_NON_GRID_CONTENT = "has_non_grid_content"
    NOT_A_DIRECTORY = "not_a_directory"


def classify_directory_state(path: Path) -> DirState:
    if not path.exists():
        return DirState.ABSENT
    if not path.is_dir():
        return DirState.NOT_A_DIRECTORY
    visible_entries = [
        entry for entry in path.iterdir() if not entry.name.startswith(".")
    ]
    if all(_GRID_NOTE_PATTERN.match(entry.name) for entry in visible_entries):
        return DirState.EMPTY_OR_VAULT
    return DirState.HAS_NON_GRID_CONTENT
