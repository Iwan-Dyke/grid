from datetime import datetime, UTC

from pytest_bdd import scenario, given, when, then, parsers

from grid.note_modeling import Note, Link
from grid.vault_parsing.sync import sync


@scenario("features/sync.feature", "Links extracted from body replace frontmatter links")
def test_sync_adds_links():
    pass


@scenario("features/sync.feature", "Unchanged links return original note")
def test_sync_unchanged():
    pass


@scenario("features/sync.feature", "Removed body link removes frontmatter link")
def test_sync_removes_links():
    pass


@scenario("features/sync.feature", "Modified timestamp updates when links change")
def test_sync_updates_modified():
    pass


@scenario("features/sync.feature", "Modified timestamp unchanged when links match")
def test_sync_modified_unchanged():
    pass


NOW = datetime(2026, 4, 9, 22, 14, 0, tzinfo=UTC)


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


@given(
    parsers.parse('a note with body "{body}" and no frontmatter links'),
    target_fixture="note",
)
def note_no_links(body):
    return make_note(body=body)


@given(
    parsers.parse('a note with body "{body}" and matching frontmatter links'),
    target_fixture="note",
)
def note_matching_links(body):
    return make_note(
        body=body,
        links=(Link(target_id="20260101120000", link_type="linksTo"),),
    )


@given(
    parsers.parse('a note with body "{body}" and a frontmatter link to "{target}"'),
    target_fixture="note",
)
def note_with_stale_link(body, target):
    return make_note(
        body=body,
        links=(Link(target_id=target, link_type="linksTo"),),
    )


@when("the note is synced", target_fixture="result")
def sync_note(note):
    return sync(note)


@then(parsers.parse('the note has {count:d} link to "{target}"'))
def check_link(result, count, target):
    assert len(result.links) == count
    assert result.links[0].target_id == target


@then(parsers.parse("the note has {count:d} links"))
def check_link_count(result, count):
    assert len(result.links) == count


@then("the original note is returned unchanged")
def check_same_object(note, result):
    assert result is note


@then("the modified timestamp is updated")
def check_modified_updated(note, result):
    assert result.modified > note.modified


@then("the modified timestamp is unchanged")
def check_modified_unchanged(note, result):
    assert result.modified == note.modified
