import pytest

from grid.note_modeling.tag import Tag, MAX_TAG_LENGTH


class TestTagCreation:
    def test_stores_name(self):
        assert Tag(name="rdf").name == "rdf"

    def test_is_frozen(self):
        tag = Tag(name="rdf")
        with pytest.raises(AttributeError):
            tag.name = "other"


class TestTagSanitisation:
    def test_lowercases(self):
        assert Tag(name="RDF").name == "rdf"

    def test_strips_leading_whitespace(self):
        assert Tag(name="  rdf").name == "rdf"

    def test_strips_trailing_whitespace(self):
        assert Tag(name="rdf  ").name == "rdf"

    def test_strips_and_lowercases(self):
        assert Tag(name="  RDF  ").name == "rdf"


class TestTagValidation:
    def test_rejects_empty(self):
        with pytest.raises(ValueError):
            Tag(name="")

    def test_rejects_whitespace_only(self):
        with pytest.raises(ValueError):
            Tag(name="   ")

    def test_rejects_interior_space(self):
        with pytest.raises(ValueError):
            Tag(name="linked data")

    def test_rejects_tab(self):
        with pytest.raises(ValueError):
            Tag(name="linked\tdata")

    def test_rejects_newline(self):
        with pytest.raises(ValueError):
            Tag(name="linked\ndata")

    def test_rejects_exceeding_max_length(self):
        with pytest.raises(ValueError):
            Tag(name="a" * (MAX_TAG_LENGTH + 1))

    def test_accepts_at_max_length(self):
        tag = Tag(name="a" * MAX_TAG_LENGTH)
        assert len(tag.name) == MAX_TAG_LENGTH


class TestTagEquality:
    def test_equal_tags(self):
        assert Tag(name="rdf") == Tag(name="rdf")

    def test_unequal_tags(self):
        assert Tag(name="rdf") != Tag(name="go")

    def test_case_insensitive_equality(self):
        assert Tag(name="RDF") == Tag(name="rdf")
