from datetime import datetime, UTC

from pytest_bdd import scenario, given, when, then, parsers

from grid.note_modeling.note import Note
from grid.note_modeling.tag import Tag
from grid.note_modeling.link import Link


@scenario("features/note.feature", "Create a valid note")
def test_valid_note():
    pass


@scenario("features/note.feature", "Empty title is rejected")
def test_empty_title():
    pass


@scenario("features/note.feature", "Modified before created is rejected")
def test_modified_before_created():
    pass


@scenario("features/note.feature", "Note with tags and links")
def test_note_with_tags_and_links():
    pass


NOW = datetime(2026, 4, 9, 22, 14, 0, tzinfo=UTC)


@given(parsers.parse('a valid note with title "{title}"'), target_fixture="note_args")
def valid_note_args(title):
    return {
        "id": "20260409221400",
        "title": title,
        "created": NOW,
        "modified": NOW,
        "tags": (),
        "links": (),
        "body": "",
    }


@given("a note with an empty title", target_fixture="note_args")
def empty_title_args():
    return {
        "id": "20260409221400",
        "title": "",
        "created": NOW,
        "modified": NOW,
        "tags": (),
        "links": (),
        "body": "",
    }


@given("a note where modified is before created", target_fixture="note_args")
def modified_before_created_args():
    return {
        "id": "20260409221400",
        "title": "Test",
        "created": NOW,
        "modified": datetime(2025, 1, 1, tzinfo=UTC),
        "tags": (),
        "links": (),
        "body": "",
    }


@given(
    parsers.parse('a note with tags "{tags}" and a link to "{target}"'),
    target_fixture="note_args",
)
def note_with_tags_and_links(tags, target):
    tag_list = tuple(Tag(name=t.strip()) for t in tags.split(","))
    return {
        "id": "20260409221400",
        "title": "Test",
        "created": NOW,
        "modified": NOW,
        "tags": tag_list,
        "links": (Link(target_id=target, link_type="linksTo"),),
        "body": "",
    }


@when("the note is created", target_fixture="note_result")
def create_note(note_args):
    try:
        return Note(**note_args)
    except ValueError as e:
        return e


@then(parsers.parse('the note title is "{expected}"'))
def check_title(note_result, expected):
    assert isinstance(note_result, Note)
    assert note_result.title == expected


@then(parsers.parse('the note type is "{expected}"'))
def check_type(note_result, expected):
    assert isinstance(note_result, Note)
    assert note_result.note_type == expected


@then("a ValueError is raised")
def check_value_error(note_result):
    assert isinstance(note_result, ValueError)


@then(parsers.parse("the note has {count:d} tags"))
def check_tag_count(note_result, count):
    assert isinstance(note_result, Note)
    assert len(note_result.tags) == count


@then(parsers.parse("the note has {count:d} link"))
def check_link_count(note_result, count):
    assert isinstance(note_result, Note)
    assert len(note_result.links) == count
