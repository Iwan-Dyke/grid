import pytest
from pytest_bdd import scenario, given, when, then, parsers

from grid.note_modeling.tag import Tag


@scenario("features/tag.feature", "Valid tag is lowercased")
def test_tag_lowercased():
    pass


@scenario("features/tag.feature", "Whitespace is rejected")
def test_tag_whitespace_rejected():
    pass


@scenario("features/tag.feature", "Empty string is rejected")
def test_tag_empty_rejected():
    pass


@scenario("features/tag.feature", "Tag exceeds max length")
def test_tag_exceeds_max_length():
    pass


@scenario("features/tag.feature", "Tag at max length is accepted")
def test_tag_at_max_length():
    pass


@scenario("features/tag.feature", "Leading and trailing whitespace is stripped")
def test_tag_whitespace_stripped():
    pass


@scenario("features/tag.feature", "Interior whitespace is still rejected after stripping")
def test_tag_interior_whitespace_rejected():
    pass


@given(parsers.parse('a tag name "{name}"'), target_fixture="tag_name")
def tag_name(name):
    return name


@given('a tag name ""', target_fixture="tag_name")
def tag_name_empty():
    return ""


@given(
    parsers.parse("a tag name that is {length:d} characters long"),
    target_fixture="tag_name",
)
def tag_name_of_length(length):
    return "a" * length


@when("the tag is created", target_fixture="tag_result")
def create_tag(tag_name):
    try:
        return Tag(name=tag_name)
    except ValueError as e:
        return e


@then(parsers.parse('the tag name is "{expected}"'))
def check_tag_name(tag_result, expected):
    assert isinstance(tag_result, Tag)
    assert tag_result.name == expected


@then("a ValueError is raised")
def check_value_error(tag_result):
    assert isinstance(tag_result, ValueError)


@then("the tag is created successfully")
def check_tag_created(tag_result):
    assert isinstance(tag_result, Tag)
