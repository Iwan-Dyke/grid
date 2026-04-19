import pytest

from grid.note_modeling.link import Link


class TestLinkCreation:
    def test_stores_fields(self):
        link = Link(target_id="20260409221400", link_type="related")
        assert link.target_id == "20260409221400"
        assert link.link_type == "related"
        assert link.label is None

    def test_stores_label(self):
        link = Link(target_id="20260409221400", link_type="related", label="see this")
        assert link.label == "see this"

    def test_is_frozen(self):
        link = Link(target_id="20260409221400", link_type="linksTo")
        with pytest.raises(AttributeError):
            link.target_id = "other"


class TestLinkTargetValidation:
    def test_rejects_empty(self):
        with pytest.raises(ValueError):
            Link(target_id="", link_type="linksTo")

    def test_rejects_non_numeric(self):
        with pytest.raises(ValueError):
            Link(target_id="not-an-id", link_type="linksTo")

    def test_rejects_wrong_length(self):
        with pytest.raises(ValueError):
            Link(target_id="2026040922", link_type="linksTo")

    def test_rejects_13_digits(self):
        with pytest.raises(ValueError):
            Link(target_id="2026040922140", link_type="linksTo")

    def test_rejects_15_digits(self):
        with pytest.raises(ValueError):
            Link(target_id="202604092214001", link_type="linksTo")

    def test_accepts_14_digits(self):
        link = Link(target_id="20260409221400", link_type="linksTo")
        assert link.target_id == "20260409221400"


class TestLinkTypeValidation:
    def test_rejects_empty(self):
        with pytest.raises(ValueError):
            Link(target_id="20260409221400", link_type="")

    def test_rejects_whitespace_only(self):
        with pytest.raises(ValueError):
            Link(target_id="20260409221400", link_type="   ")

    def test_strips_whitespace(self):
        link = Link(target_id="20260409221400", link_type="  related  ")
        assert link.link_type == "related"

    def test_accepts_custom_type(self):
        link = Link(target_id="20260409221400", link_type="inspiredBy")
        assert link.link_type == "inspiredBy"

    def test_accepts_known_types(self):
        for t in ("linksTo", "related", "broader", "narrower", "seeAlso"):
            link = Link(target_id="20260409221400", link_type=t)
            assert link.link_type == t

    def test_rejects_hyphen(self):
        with pytest.raises(ValueError):
            Link(target_id="20260409221400", link_type="see-also")

    def test_rejects_double_colon(self):
        with pytest.raises(ValueError):
            Link(target_id="20260409221400", link_type="see::also")

    def test_rejects_space(self):
        with pytest.raises(ValueError):
            Link(target_id="20260409221400", link_type="see also")

    def test_accepts_underscore(self):
        link = Link(target_id="20260409221400", link_type="see_also")
        assert link.link_type == "see_also"

    def test_accepts_digits(self):
        link = Link(target_id="20260409221400", link_type="refersTo2")
        assert link.link_type == "refersTo2"


class TestLinkEquality:
    def test_equal_links(self):
        a = Link(target_id="20260409221400", link_type="related")
        b = Link(target_id="20260409221400", link_type="related")
        assert a == b

    def test_different_target(self):
        a = Link(target_id="20260409221400", link_type="related")
        b = Link(target_id="20260101120000", link_type="related")
        assert a != b

    def test_different_type(self):
        a = Link(target_id="20260409221400", link_type="related")
        b = Link(target_id="20260409221400", link_type="broader")
        assert a != b
