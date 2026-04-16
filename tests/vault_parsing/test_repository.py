from datetime import datetime, UTC

from pytest_bdd import scenario, given, when, then, parsers

from grid.note_modeling import Note
from grid.vault_parsing.repository import MarkdownFileRepository
from grid.vault_parsing.errors import NoteNotFoundError, NoteParseError


NOW = datetime(2026, 4, 9, 22, 14, 0, tzinfo=UTC)

IDS = [
    "20260409221400",
    "20260409221401",
    "20260409221402",
]


def make_note(index=0, title="My Note", tags=(), links=(), body="Some content"):
    return Note(
        id=IDS[index],
        title=title,
        created=NOW,
        modified=NOW,
        tags=tags,
        links=links,
        body=body,
    )


@scenario("features/repository.feature", "Save and load a note")
def test_save_and_load():
    pass


@scenario("features/repository.feature", "Load all notes")
def test_load_all():
    pass


@scenario("features/repository.feature", "Delete a note")
def test_delete():
    pass


@scenario("features/repository.feature", "Check existence")
def test_existence():
    pass


@scenario("features/repository.feature", "Load raw file contents")
def test_load_raw():
    pass


@scenario("features/repository.feature", "Load nonexistent note raises error")
def test_load_nonexistent():
    pass


@scenario("features/repository.feature", "Malformed frontmatter raises error")
def test_malformed():
    pass


@given("an empty vault", target_fixture="repo")
def empty_vault(tmp_path):
    return MarkdownFileRepository(tmp_path)


@given("a vault with 3 notes", target_fixture="repo")
def vault_with_three(tmp_path):
    repo = MarkdownFileRepository(tmp_path)
    for i in range(3):
        repo.save(make_note(index=i, title=f"Note {i}"))
    return repo


@given("a vault with a saved note", target_fixture="repo")
def vault_with_note(tmp_path):
    repo = MarkdownFileRepository(tmp_path)
    repo.save(make_note())
    return repo


@given("a vault with a malformed markdown file", target_fixture="repo")
def vault_with_malformed(tmp_path):
    bad_file = tmp_path / "20260409221400-bad.md"
    bad_file.write_text("---\nid: 123\n--BROKEN--\n")
    return MarkdownFileRepository(tmp_path)


@when('I save a note with title "My Note"', target_fixture="saved_note")
def save_note(repo):
    note = make_note()
    repo.save(note)
    return note


@when("I load the note by ID", target_fixture="loaded_note")
def load_by_id(repo, saved_note):
    return repo.load(saved_note.id)


@when("I load all notes", target_fixture="load_result")
def load_all(repo):
    try:
        return repo.load_all()
    except NoteParseError as e:
        return e


@when("I delete the note")
def delete_note(repo):
    repo.delete(IDS[0])


@when("I load the raw contents", target_fixture="raw")
def load_raw(repo):
    return repo.load_raw(IDS[0])


@when("I load a nonexistent note", target_fixture="load_result")
def load_nonexistent(repo):
    try:
        return repo.load("99999999999999")
    except NoteNotFoundError as e:
        return e


@then(parsers.parse('the loaded note has title "{title}"'))
def check_title(loaded_note, title):
    assert loaded_note.title == title


@then(parsers.parse("{count:d} notes are returned"))
def check_count(load_result, count):
    assert len(load_result) == count


@then("the note no longer exists")
def check_deleted(repo):
    assert not repo.exists(IDS[0])


@then("the note exists")
def check_exists(repo):
    assert repo.exists(IDS[0])


@then("a nonexistent note does not exist")
def check_not_exists(repo):
    assert not repo.exists("99999999999999")


@then("the raw contents contain frontmatter and body")
def check_raw(raw):
    assert "---" in raw
    assert "My Note" in raw
    assert "Some content" in raw


@then("a NoteNotFoundError is raised")
def check_not_found(load_result):
    assert isinstance(load_result, NoteNotFoundError)


@then("a NoteParseError is raised")
def check_parse_error(load_result):
    assert isinstance(load_result, NoteParseError)
