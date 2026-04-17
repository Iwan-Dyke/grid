import pytest
from datetime import datetime, UTC

from grid.note_modeling import Note


NOW = datetime(2026, 4, 9, 22, 14, 0, tzinfo=UTC)


@pytest.fixture
def now():
    return NOW


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
