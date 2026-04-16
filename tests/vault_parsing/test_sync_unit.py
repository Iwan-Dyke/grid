from datetime import datetime, UTC

from grid.note_modeling import Note, Link
from grid.vault_parsing.sync import sync


NOW = datetime(2026, 4, 9, 22, 14, 0, tzinfo=UTC)
LATER = datetime(2026, 4, 10, 0, 0, 0, tzinfo=UTC)


def make_note(body="", links=()):
    return Note(
        id="20260409221400",
        title="Test",
        created=NOW,
        modified=NOW,
        tags=(),
        links=links,
        body=body,
    )


class TestSyncAddsLinks:
    def test_extracts_link_from_body(self):
        note = make_note(body="See [[20260101120000]]")
        result = sync(note, now=LATER)
        assert len(result.note.links) == 1
        assert result.note.links[0].target_id == "20260101120000"
        assert result.note.links[0].link_type == "linksTo"

    def test_extracts_typed_link(self):
        note = make_note(body="[[related::20260101120000]]")
        result = sync(note, now=LATER)
        assert result.note.links[0].link_type == "related"

    def test_extracts_labelled_link(self):
        note = make_note(body="[[related::20260101120000|see this]]")
        result = sync(note, now=LATER)
        assert result.note.links[0].label == "see this"


class TestSyncRemovesLinks:
    def test_removes_stale_link(self):
        note = make_note(
            body="No links",
            links=(Link(target_id="20260101120000", link_type="linksTo"),),
        )
        result = sync(note, now=LATER)
        assert len(result.note.links) == 0

    def test_full_replace(self):
        note = make_note(
            body="[[20260101120000]]",
            links=(Link(target_id="99999999999999", link_type="related"),),
        )
        result = sync(note, now=LATER)
        assert len(result.note.links) == 1
        assert result.note.links[0].target_id == "20260101120000"


class TestSyncUnchanged:
    def test_returns_same_note_when_unchanged(self):
        links = (Link(target_id="20260101120000", link_type="linksTo"),)
        note = make_note(body="[[20260101120000]]", links=links)
        result = sync(note, now=LATER)
        assert result.note is note
        assert not result.changed

    def test_no_links_stays_unchanged(self):
        note = make_note(body="Plain text", links=())
        result = sync(note, now=LATER)
        assert result.note is note
        assert not result.changed


class TestSyncModifiedTimestamp:
    def test_bumps_modified_on_change(self):
        note = make_note(body="[[20260101120000]]")
        result = sync(note, now=LATER)
        assert result.note.modified == LATER

    def test_preserves_modified_when_unchanged(self):
        links = (Link(target_id="20260101120000", link_type="linksTo"),)
        note = make_note(body="[[20260101120000]]", links=links)
        result = sync(note, now=LATER)
        assert result.note.modified == note.modified

    def test_preserves_created(self):
        note = make_note(body="[[20260101120000]]")
        result = sync(note, now=LATER)
        assert result.note.created == note.created


class TestSyncAmbiguous:
    def test_surfaces_ambiguous_links(self):
        note = make_note(body="[[20260101120000|some label]]")
        result = sync(note, now=LATER)
        assert len(result.ambiguous) == 1
        assert result.ambiguous[0].label == "some label"

    def test_no_ambiguity_for_typed_links(self):
        note = make_note(body="[[related::20260101120000|see this]]")
        result = sync(note, now=LATER)
        assert result.ambiguous == []

    def test_changed_is_true(self):
        note = make_note(body="[[20260101120000]]")
        result = sync(note, now=LATER)
        assert result.changed
