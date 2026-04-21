from pytest_bdd import scenario, given, when, then, parsers

from grid.vault_parsing.wiki_links import extract_wiki_links


@scenario("features/wiki_links.feature", "Plain link")
def test_plain_link():
    pass


@scenario("features/wiki_links.feature", "Typed link")
def test_typed_link():
    pass


@scenario("features/wiki_links.feature", "Typed link with label")
def test_typed_link_with_label():
    pass


@scenario("features/wiki_links.feature", "Multiple links in one body")
def test_multiple_links():
    pass


@scenario("features/wiki_links.feature", "No links in body")
def test_no_links():
    pass


@scenario("features/wiki_links.feature", "Label without type is ambiguous")
def test_label_without_type():
    pass


@given(parsers.parse('a body containing "{body}"'), target_fixture="body")
def body_text(body):
    return body


@when("wiki-links are extracted", target_fixture="result")
def extract(body):
    return extract_wiki_links(body)


@then(parsers.parse("{count:d} link is found"))
def check_single_count(result, count):
    assert len(result.links) == count


@then(parsers.parse("{count:d} links are found"))
def check_count(result, count):
    assert len(result.links) == count


@then(
    parsers.parse('the link has target "{target}" and type "{link_type}" and no label')
)
def check_link_no_label(result, target, link_type):
    link = result.links[0]
    assert link.target_id == target
    assert link.link_type == link_type
    assert link.label is None


@then(
    parsers.parse(
        'the link has target "{target}" and type "{link_type}" and label "{label}"'
    )
)
def check_link_with_label(result, target, link_type, label):
    link = result.links[0]
    assert link.target_id == target
    assert link.link_type == link_type
    assert link.label == label


@then("the ambiguity is flagged")
def check_ambiguous(result):
    assert len(result.ambiguous) == 1
    assert result.ambiguous[0].target_id == "20260409221400"
    assert result.ambiguous[0].label == "some label"
