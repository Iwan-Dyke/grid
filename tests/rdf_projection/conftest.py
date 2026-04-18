from datetime import UTC, datetime

import pytest

from grid.note_modeling import Note, Tag

NOW = datetime(2026, 4, 9, 22, 14, 0, tzinfo=UTC)
LATER = datetime(2026, 4, 10, 0, 0, 0, tzinfo=UTC)


def make_note(
    id="20260409221400",
    title="Test Note",
    tags=(),
    links=(),
    body="",
    note_type="note",
    created=NOW,
    modified=NOW,
):
    return Note(
        id=id,
        title=title,
        note_type=note_type,
        created=created,
        modified=modified,
        tags=tags,
        links=links,
        body=body,
    )


@pytest.fixture
def note():
    return make_note()


@pytest.fixture
def note_with_tags():
    return make_note(tags=(Tag(name="rdf"), Tag(name="linked-data")))


@pytest.fixture
def two_notes():
    a = make_note(id="20260409221400", title="A")
    b = make_note(id="20260101120000", title="B")
    return [a, b]


@pytest.fixture
def make():
    return make_note
