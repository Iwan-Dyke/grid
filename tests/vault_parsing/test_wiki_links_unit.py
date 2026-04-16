from grid.note_modeling import Link
from grid.vault_parsing.wiki_links import extract_wiki_links


class TestPlainLinks:
    def test_extracts_plain_link(self):
        links = extract_wiki_links("See [[20260409221400]]")
        assert len(links) == 1
        assert links[0] == Link(target_id="20260409221400", link_type="linksTo")

    def test_defaults_to_links_to(self):
        links = extract_wiki_links("[[20260409221400]]")
        assert links[0].link_type == "linksTo"


class TestTypedLinks:
    def test_extracts_typed_link(self):
        links = extract_wiki_links("[[related::20260409221400]]")
        assert links[0].link_type == "related"
        assert links[0].target_id == "20260409221400"

    def test_broader(self):
        links = extract_wiki_links("[[broader::20260409221400]]")
        assert links[0].link_type == "broader"

    def test_narrower(self):
        links = extract_wiki_links("[[narrower::20260409221400]]")
        assert links[0].link_type == "narrower"

    def test_see_also(self):
        links = extract_wiki_links("[[seeAlso::20260409221400]]")
        assert links[0].link_type == "seeAlso"

    def test_custom_type(self):
        links = extract_wiki_links("[[inspiredBy::20260409221400]]")
        assert links[0].link_type == "inspiredBy"


class TestLabels:
    def test_typed_with_label(self):
        links = extract_wiki_links("[[related::20260409221400|see this]]")
        assert links[0].label == "see this"

    def test_label_without_type_ignored(self):
        links = extract_wiki_links("[[20260409221400|some label]]")
        assert links[0].link_type == "linksTo"
        assert links[0].label is None


class TestMultipleLinks:
    def test_extracts_all(self):
        body = "[[20260409221400]] then [[related::20260101120000]]"
        links = extract_wiki_links(body)
        assert len(links) == 2
        assert links[0].target_id == "20260409221400"
        assert links[1].target_id == "20260101120000"

    def test_deduplicates_same_link(self):
        body = "[[20260409221400]] and [[20260409221400]]"
        links = extract_wiki_links(body)
        assert len(links) == 1


class TestEdgeCases:
    def test_empty_body(self):
        assert extract_wiki_links("") == []

    def test_no_links(self):
        assert extract_wiki_links("Just plain text") == []

    def test_malformed_id_ignored(self):
        assert extract_wiki_links("[[notanid]]") == []

    def test_link_in_multiline_body(self):
        body = "First line\n\nSee [[20260409221400]]\n\nLast line"
        links = extract_wiki_links(body)
        assert len(links) == 1
