import pytest
from datetime import datetime, UTC

from grid.note_modeling import Tag, Link
from grid.vault_parsing.parser import (
    parse_note,
    serialize_note,
    serialize_link,
    deserialize_link,
    parse_datetime,
)
from grid.vault_parsing.errors import NoteParseError

from tests.vault_parsing.conftest import make_note


class TestParseDateTime:
    def test_parses_iso_string(self):
        result = parse_datetime("2026-04-09T22:14:00+00:00")
        assert result == datetime(2026, 4, 9, 22, 14, 0, tzinfo=UTC)

    def test_handles_datetime_with_utc_tz(self):
        dt = datetime(2026, 4, 9, 22, 14, 0, tzinfo=UTC)
        assert parse_datetime(dt) == dt

    def test_converts_non_utc_datetime_to_utc(self):
        from datetime import timezone, timedelta
        plus_two = timezone(timedelta(hours=2))
        dt = datetime(2026, 4, 9, 22, 14, 0, tzinfo=plus_two)
        result = parse_datetime(dt)
        assert result == datetime(2026, 4, 9, 20, 14, 0, tzinfo=UTC)
        assert result.tzinfo is UTC

    def test_converts_non_utc_iso_string_to_utc(self):
        result = parse_datetime("2026-04-09T22:14:00+02:00")
        assert result == datetime(2026, 4, 9, 20, 14, 0, tzinfo=UTC)
        assert result.tzinfo is UTC

    def test_adds_utc_to_naive_datetime(self):
        naive = datetime(2026, 4, 9, 22, 14, 0)
        result = parse_datetime(naive)
        assert result.tzinfo is UTC

    def test_preserves_value_for_naive(self):
        naive = datetime(2026, 4, 9, 22, 14, 0)
        result = parse_datetime(naive)
        assert result.year == 2026
        assert result.hour == 22


class TestSerializeLink:
    def test_without_label(self):
        link = Link(target_id="20260409221400", link_type="related")
        result = serialize_link(link)
        assert result == {"id": "20260409221400", "type": "related"}
        assert "label" not in result

    def test_with_label(self):
        link = Link(target_id="20260409221400", link_type="related", label="see this")
        result = serialize_link(link)
        assert result["label"] == "see this"


class TestDeserializeLink:
    def test_without_label(self):
        link = deserialize_link({"id": "20260409221400", "type": "related"})
        assert link == Link(target_id="20260409221400", link_type="related")

    def test_with_label(self):
        link = deserialize_link({"id": "20260409221400", "type": "related", "label": "see this"})
        assert link.label == "see this"

    def test_round_trip(self):
        original = Link(target_id="20260409221400", link_type="broader", label="parent")
        result = deserialize_link(serialize_link(original))
        assert result == original


class TestSerializeNote:
    def test_contains_frontmatter(self):
        note = make_note()
        result = serialize_note(note)
        assert "---" in result
        assert "Test Note" in result

    def test_contains_body(self):
        note = make_note(body="Some content here")
        result = serialize_note(note)
        assert "Some content here" in result


class TestParseNote:
    def test_round_trip(self, tmp_path):
        note = make_note()
        path = tmp_path / "test.md"
        path.write_text(serialize_note(note))
        loaded = parse_note(path)
        assert loaded.id == note.id
        assert loaded.title == note.title
        assert loaded.body == note.body

    def test_round_trip_with_tags_and_links(self, tmp_path):
        note = make_note(
            tags=(Tag(name="rdf"),),
            links=(Link(target_id="20260101120000", link_type="related"),),
        )
        path = tmp_path / "test.md"
        path.write_text(serialize_note(note))
        loaded = parse_note(path)
        assert loaded.tags == note.tags
        assert loaded.links == note.links

    def test_defaults_type_to_note(self, tmp_path):
        path = tmp_path / "test.md"
        path.write_text(
            "---\nid: '20260409221400'\ntitle: Test\n"
            "created: '2026-04-09T22:14:00+00:00'\n"
            "modified: '2026-04-09T22:14:00+00:00'\n---\n"
        )
        loaded = parse_note(path)
        assert loaded.note_type == "note"

    def test_missing_id_raises(self, tmp_path):
        path = tmp_path / "test.md"
        path.write_text("---\ntitle: Test\n---\nBody\n")
        with pytest.raises(NoteParseError):
            parse_note(path)

    def test_missing_title_raises(self, tmp_path):
        path = tmp_path / "test.md"
        path.write_text("---\nid: '20260409221400'\n---\nBody\n")
        with pytest.raises(NoteParseError):
            parse_note(path)
