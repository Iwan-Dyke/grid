from datetime import datetime

from pytest_bdd import scenario, given, when, then, parsers

from grid.vault_parsing.errors import NoteParseError
from grid.vault_parsing.parser import parse_note, serialize_note

from tests.vault_parsing.conftest import make_note


@scenario("features/parser.feature", "Round-trip preserves all fields")
def test_round_trip():
    pass


@scenario("features/parser.feature", "Missing id raises a parse error")
def test_missing_id():
    pass


@scenario("features/parser.feature", "Missing title raises a parse error")
def test_missing_title():
    pass


@scenario("features/parser.feature", "A non-UTC timestamp is converted to UTC")
def test_non_utc_timestamp():
    pass


@scenario("features/parser.feature", "A naive timestamp is tagged as UTC")
def test_naive_timestamp():
    pass


@given("a Note serialized to a markdown file", target_fixture="context")
def note_file(tmp_path):
    note = make_note()
    path = tmp_path / "20260409221400-test.md"
    path.write_text(serialize_note(note))
    return {"path": path, "original": note}


@given(
    parsers.parse('a markdown file with frontmatter "{frontmatter}"'),
    target_fixture="context",
)
def bad_frontmatter(tmp_path, frontmatter):
    content = "---\n" + frontmatter.encode().decode("unicode_escape") + "---\nBody\n"
    path = tmp_path / "bad.md"
    path.write_text(content)
    return {"path": path}


@given(
    parsers.parse('a markdown file with created timestamp "{ts}"'),
    target_fixture="context",
)
def file_with_timestamp(tmp_path, ts):
    content = (
        "---\n"
        "id: '20260409221400'\n"
        "title: Test\n"
        f"created: '{ts}'\n"
        f"modified: '{ts}'\n"
        "---\nBody\n"
    )
    path = tmp_path / "20260409221400-test.md"
    path.write_text(content)
    return {"path": path}


@when("I parse the file", target_fixture="result")
def parse(context):
    try:
        return parse_note(context["path"])
    except NoteParseError as e:
        return e


@then("the loaded note equals the original")
def check_equal(result, context):
    assert result == context["original"]


@then("a NoteParseError is raised")
def check_parse_error(result):
    assert isinstance(result, NoteParseError)


@then(parsers.parse("the loaded note's created timestamp is \"{expected}\""))
def check_created(result, expected):
    assert result.created == datetime.fromisoformat(expected)
