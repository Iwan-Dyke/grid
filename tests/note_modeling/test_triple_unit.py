import pytest

from grid.note_modeling.triple import IRI, Triple, TypedLiteral


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


class TestIRI:
    def test_is_str_subclass(self):
        assert isinstance(IRI("http://example.com"), str)

    def test_equals_underlying_string(self):
        assert IRI("http://example.com") == "http://example.com"

    def test_isinstance_check_distinguishes_from_str(self):
        assert isinstance(IRI("x"), IRI)
        assert not isinstance("x", IRI)


class TestTypedLiteral:
    def test_is_str_subclass(self):
        assert isinstance(TypedLiteral("2026-04-09", "http://xsd/date"), str)

    def test_stores_datatype(self):
        tl = TypedLiteral("2026-04-09T22:14:00", "http://xsd/dateTime")
        assert tl.datatype == "http://xsd/dateTime"

    def test_equals_underlying_string(self):
        tl = TypedLiteral("2026-04-09", "http://xsd/date")
        assert tl == "2026-04-09"

    def test_isinstance_check_distinguishes_from_str(self):
        tl = TypedLiteral("x", "http://xsd/string")
        assert isinstance(tl, TypedLiteral)
        assert not isinstance("x", TypedLiteral)

    def test_usable_as_triple_object(self):
        tl = TypedLiteral("2026-04-09", "http://xsd/date")
        triple = Triple(subject="grid:123", predicate="dcterms:date", object=tl)
        assert triple.object.datatype == "http://xsd/date"
