import pytest
from datetime import datetime, UTC

from grid.note_modeling import Note, Tag, Link, NoteRepository
from grid.vault_parsing.repository import MarkdownFileRepository
from grid.vault_parsing.errors import NoteNotFoundError, NoteParseError

from tests.vault_parsing.conftest import make_note


class TestProtocolConformance:
    def test_satisfies_note_repository(self, tmp_path):
        assert isinstance(MarkdownFileRepository(tmp_path), NoteRepository)


class TestSaveAndLoad:
    def test_round_trip(self, tmp_path):
        repo = MarkdownFileRepository(tmp_path)
        note = make_note()
        repo.save(note)
        loaded = repo.load(note.id)
        assert loaded.id == note.id
        assert loaded.title == note.title
        assert loaded.body == note.body

    def test_preserves_tags(self, tmp_path):
        repo = MarkdownFileRepository(tmp_path)
        note = make_note(tags=(Tag(name="rdf"), Tag(name="python")))
        repo.save(note)
        loaded = repo.load(note.id)
        assert loaded.tags == note.tags

    def test_preserves_links(self, tmp_path):
        repo = MarkdownFileRepository(tmp_path)
        note = make_note(links=(
            Link(target_id="20260101120000", link_type="related", label="see this"),
        ))
        repo.save(note)
        loaded = repo.load(note.id)
        assert loaded.links == note.links

    def test_preserves_timestamps(self, tmp_path):
        repo = MarkdownFileRepository(tmp_path)
        note = make_note()
        repo.save(note)
        loaded = repo.load(note.id)
        assert loaded.created == note.created
        assert loaded.modified == note.modified

    def test_preserves_note_type(self, tmp_path):
        repo = MarkdownFileRepository(tmp_path)
        note = make_note(note_type="reference")
        repo.save(note)
        loaded = repo.load(note.id)
        assert loaded.note_type == "reference"

    def test_overwrites_on_second_save(self, tmp_path):
        repo = MarkdownFileRepository(tmp_path)
        note = make_note(body="original")
        repo.save(note)
        updated = Note(
            id=note.id,
            title=note.title,
            created=note.created,
            modified=datetime(2026, 4, 10, 0, 0, 0, tzinfo=UTC),
            tags=note.tags,
            links=note.links,
            body="updated",
        )
        repo.save(updated)
        loaded = repo.load(note.id)
        assert loaded.body == "updated"

    def test_title_rename_removes_old_file(self, tmp_path):
        repo = MarkdownFileRepository(tmp_path)
        note = make_note(title="Original Title")
        repo.save(note)
        old_files = list(tmp_path.glob("*.md"))
        assert len(old_files) == 1
        renamed = Note(
            id=note.id,
            title="New Title",
            created=note.created,
            modified=datetime(2026, 4, 10, 0, 0, 0, tzinfo=UTC),
            tags=note.tags,
            links=note.links,
            body=note.body,
        )
        repo.save(renamed)
        files = list(tmp_path.glob("*.md"))
        assert len(files) == 1
        assert "new-title" in files[0].name

    def test_unicode_round_trip(self, tmp_path):
        repo = MarkdownFileRepository(tmp_path)
        note = make_note(title="Uber Cool", body="Content with unicode: cafe")
        repo.save(note)
        loaded = repo.load(note.id)
        assert loaded.body == note.body


class TestLoadAll:
    def test_returns_all_notes(self, tmp_path):
        repo = MarkdownFileRepository(tmp_path)
        repo.save(make_note(id="20260409221400"))
        repo.save(make_note(id="20260409221401", title="Second"))
        result = repo.load_all()
        assert len(result) == 2

    def test_empty_vault(self, tmp_path):
        repo = MarkdownFileRepository(tmp_path)
        assert repo.load_all() == []


class TestLoadRaw:
    def test_returns_file_contents(self, tmp_path):
        repo = MarkdownFileRepository(tmp_path)
        repo.save(make_note())
        raw = repo.load_raw("20260409221400")
        assert "---" in raw
        assert "Test Note" in raw
        assert "Hello world" in raw

    def test_nonexistent_raises(self, tmp_path):
        repo = MarkdownFileRepository(tmp_path)
        with pytest.raises(NoteNotFoundError):
            repo.load_raw("99999999999999")


class TestDelete:
    def test_removes_file(self, tmp_path):
        repo = MarkdownFileRepository(tmp_path)
        repo.save(make_note())
        repo.delete("20260409221400")
        assert not repo.exists("20260409221400")

    def test_delete_nonexistent_raises(self, tmp_path):
        repo = MarkdownFileRepository(tmp_path)
        with pytest.raises(NoteNotFoundError):
            repo.delete("99999999999999")


class TestExists:
    def test_exists_after_save(self, tmp_path):
        repo = MarkdownFileRepository(tmp_path)
        repo.save(make_note())
        assert repo.exists("20260409221400")

    def test_not_exists(self, tmp_path):
        repo = MarkdownFileRepository(tmp_path)
        assert not repo.exists("99999999999999")


class TestDuplicateId:
    def test_load_all_raises_on_duplicate(self, tmp_path):
        repo = MarkdownFileRepository(tmp_path)
        repo.save(make_note(title="First"))
        dupe_file = tmp_path / "20260409221400-duplicate.md"
        original = list(tmp_path.glob("20260409221400-*.md"))[0]
        dupe_file.write_text(original.read_text())
        with pytest.raises(NoteParseError):
            repo.load_all()


class TestErrorHandling:
    def test_load_nonexistent_raises(self, tmp_path):
        repo = MarkdownFileRepository(tmp_path)
        with pytest.raises(NoteNotFoundError):
            repo.load("99999999999999")

    def test_malformed_frontmatter_raises(self, tmp_path):
        bad_file = tmp_path / "20260409221400-bad.md"
        bad_file.write_text("---\nid: 123\n--BROKEN--\n")
        repo = MarkdownFileRepository(tmp_path)
        with pytest.raises(NoteParseError):
            repo.load_all()
