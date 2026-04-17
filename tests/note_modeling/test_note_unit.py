import pytest
from datetime import datetime, UTC

from grid.note_modeling import Tag, Link

from tests.note_modeling.conftest import make_note, NOW


class TestNoteCreation:
    def test_stores_fields(self):
        note = make_note()
        assert note.id == "20260409221400"
        assert note.title == "Test Note"
        assert note.note_type == "note"
        assert note.created == NOW
        assert note.modified == NOW
        assert note.tags == ()
        assert note.links == ()
        assert note.body == ""

    def test_default_note_type(self):
        note = make_note()
        assert note.note_type == "note"

    def test_custom_note_type(self):
        note = make_note(note_type="reference")
        assert note.note_type == "reference"

    def test_is_frozen(self):
        note = make_note()
        with pytest.raises(AttributeError):
            note.title = "other"


class TestNoteIdValidation:
    def test_rejects_empty_id(self):
        with pytest.raises(ValueError):
            make_note(id="")

    def test_rejects_invalid_id(self):
        with pytest.raises(ValueError):
            make_note(id="not-valid")

    def test_rejects_short_id(self):
        with pytest.raises(ValueError):
            make_note(id="2026040922")


class TestNoteTitleValidation:
    def test_rejects_empty_title(self):
        with pytest.raises(ValueError):
            make_note(title="")

    def test_rejects_whitespace_only_title(self):
        with pytest.raises(ValueError):
            make_note(title="   ")

    def test_strips_title_whitespace(self):
        note = make_note(title="  My Note  ")
        assert note.title == "My Note"


class TestNoteTypeValidation:
    def test_rejects_whitespace_only(self):
        with pytest.raises(ValueError):
            make_note(note_type="   ")

    def test_strips_whitespace(self):
        note = make_note(note_type="  reference  ")
        assert note.note_type == "reference"


class TestNoteTimestampValidation:
    def test_modified_equals_created(self):
        note = make_note(created=NOW, modified=NOW)
        assert note.modified == note.created

    def test_modified_after_created(self):
        later = datetime(2026, 4, 10, 0, 0, 0, tzinfo=UTC)
        note = make_note(created=NOW, modified=later)
        assert note.modified > note.created

    def test_rejects_modified_before_created(self):
        earlier = datetime(2025, 1, 1, tzinfo=UTC)
        with pytest.raises(ValueError):
            make_note(created=NOW, modified=earlier)


class TestNoteComposition:
    def test_with_tags(self):
        tags = (Tag(name="rdf"), Tag(name="python"))
        note = make_note(tags=tags)
        assert len(note.tags) == 2
        assert note.tags[0].name == "rdf"

    def test_with_links(self):
        links = (Link(target_id="20260101120000", link_type="related"),)
        note = make_note(links=links)
        assert len(note.links) == 1
        assert note.links[0].link_type == "related"


class TestNoteEquality:
    def test_equal_notes(self):
        assert make_note() == make_note()

    def test_different_id(self):
        assert make_note(id="20260409221400") != make_note(id="20260101120000")
