from grid.note_modeling import Link
from grid.vault_parsing.wiki_links import extract_wiki_links


class TestPlainLinks:
    def test_extracts_plain_link(self):
        result = extract_wiki_links("See [[20260409221400]]")
        assert len(result.links) == 1
        assert result.links[0] == Link(target_id="20260409221400", link_type="linksTo")

    def test_defaults_to_links_to(self):
        result = extract_wiki_links("[[20260409221400]]")
        assert result.links[0].link_type == "linksTo"


class TestTypedLinks:
    def test_extracts_typed_link(self):
        result = extract_wiki_links("[[related::20260409221400]]")
        assert result.links[0].link_type == "related"
        assert result.links[0].target_id == "20260409221400"

    def test_broader(self):
        result = extract_wiki_links("[[broader::20260409221400]]")
        assert result.links[0].link_type == "broader"

    def test_narrower(self):
        result = extract_wiki_links("[[narrower::20260409221400]]")
        assert result.links[0].link_type == "narrower"

    def test_see_also(self):
        result = extract_wiki_links("[[seeAlso::20260409221400]]")
        assert result.links[0].link_type == "seeAlso"

    def test_custom_type(self):
        result = extract_wiki_links("[[inspiredBy::20260409221400]]")
        assert result.links[0].link_type == "inspiredBy"


class TestLabels:
    def test_typed_with_label(self):
        result = extract_wiki_links("[[related::20260409221400|see this]]")
        assert result.links[0].label == "see this"

    def test_label_without_type_creates_link_without_label(self):
        result = extract_wiki_links("[[20260409221400|some label]]")
        assert result.links[0].link_type == "linksTo"
        assert result.links[0].label is None


class TestAmbiguous:
    def test_flags_label_without_type(self):
        result = extract_wiki_links("[[20260409221400|some label]]")
        assert len(result.ambiguous) == 1
        assert result.ambiguous[0].target_id == "20260409221400"
        assert result.ambiguous[0].label == "some label"
        assert result.ambiguous[0].raw == "[[20260409221400|some label]]"

    def test_no_ambiguity_for_typed_label(self):
        result = extract_wiki_links("[[related::20260409221400|see this]]")
        assert result.ambiguous == ()

    def test_no_ambiguity_for_plain_link(self):
        result = extract_wiki_links("[[20260409221400]]")
        assert result.ambiguous == ()

    def test_multiple_ambiguous(self):
        body = "[[20260409221400|label1]] and [[20260101120000|label2]]"
        result = extract_wiki_links(body)
        assert len(result.ambiguous) == 2


class TestMultipleLinks:
    def test_extracts_all(self):
        body = "[[20260409221400]] then [[related::20260101120000]]"
        result = extract_wiki_links(body)
        assert len(result.links) == 2
        assert result.links[0].target_id == "20260409221400"
        assert result.links[1].target_id == "20260101120000"

    def test_deduplicates_same_link(self):
        body = "[[20260409221400]] and [[20260409221400]]"
        result = extract_wiki_links(body)
        assert len(result.links) == 1


class TestEdgeCases:
    def test_empty_body(self):
        assert extract_wiki_links("").links == ()

    def test_no_links(self):
        assert extract_wiki_links("Just plain text").links == ()

    def test_malformed_id_ignored(self):
        assert extract_wiki_links("[[notanid]]").links == ()

    def test_link_in_multiline_body(self):
        body = "First line\n\nSee [[20260409221400]]\n\nLast line"
        result = extract_wiki_links(body)
        assert len(result.links) == 1
