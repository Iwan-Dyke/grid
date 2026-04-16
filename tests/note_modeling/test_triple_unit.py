import pytest

from grid.note_modeling.triple import Triple


class TestTripleCreation:
    def test_stores_fields(self):
        t = Triple(subject="grid:123", predicate="grid:linksTo", object="grid:456")
        assert t.subject == "grid:123"
        assert t.predicate == "grid:linksTo"
        assert t.object == "grid:456"

    def test_is_frozen(self):
        t = Triple(subject="grid:123", predicate="grid:linksTo", object="grid:456")
        with pytest.raises(AttributeError):
            t.subject = "other"


class TestTripleValidation:
    def test_rejects_empty_subject(self):
        with pytest.raises(ValueError):
            Triple(subject="", predicate="grid:linksTo", object="grid:456")

    def test_rejects_empty_predicate(self):
        with pytest.raises(ValueError):
            Triple(subject="grid:123", predicate="", object="grid:456")

    def test_rejects_empty_object(self):
        with pytest.raises(ValueError):
            Triple(subject="grid:123", predicate="grid:linksTo", object="")


class TestTripleEquality:
    def test_equal(self):
        a = Triple(subject="grid:123", predicate="grid:linksTo", object="grid:456")
        b = Triple(subject="grid:123", predicate="grid:linksTo", object="grid:456")
        assert a == b

    def test_different_subject(self):
        a = Triple(subject="grid:123", predicate="grid:linksTo", object="grid:456")
        b = Triple(subject="grid:789", predicate="grid:linksTo", object="grid:456")
        assert a != b
