from pytest_bdd import scenario, given, when, then, parsers

from grid.note_modeling.link import Link


@scenario("features/link.feature", "Valid link with default type")
def test_valid_link():
    pass


@scenario("features/link.feature", "Valid link with label")
def test_link_with_label():
    pass


@scenario("features/link.feature", "Invalid target ID rejected")
def test_invalid_target_id():
    pass


@scenario("features/link.feature", "Empty target ID rejected")
def test_empty_target_id():
    pass


@scenario("features/link.feature", "Empty link type rejected")
def test_empty_link_type():
    pass


@scenario("features/link.feature", "Custom link type accepted")
def test_custom_link_type():
    pass


@given(
    parsers.parse('a link to "{target}" with type "{link_type}"'),
    target_fixture="link_args",
)
def link_args(target, link_type):
    return {"target_id": target, "link_type": link_type}


@given('a link to "" with type "linksTo"', target_fixture="link_args")
def link_args_empty_target():
    return {"target_id": "", "link_type": "linksTo"}


@given('a link to "20260409221400" with type ""', target_fixture="link_args")
def link_args_empty_type():
    return {"target_id": "20260409221400", "link_type": ""}


@given(
    parsers.parse('a link to "{target}" with type "{link_type}" and label "{label}"'),
    target_fixture="link_args",
)
def link_args_with_label(target, link_type, label):
    return {"target_id": target, "link_type": link_type, "label": label}


@when("the link is created", target_fixture="link_result")
def create_link(link_args):
    try:
        return Link(**link_args)
    except ValueError as e:
        return e


@then(parsers.parse('the link target is "{expected}"'))
def check_target(link_result, expected):
    assert isinstance(link_result, Link)
    assert link_result.target_id == expected


@then(parsers.parse('the link type is "{expected}"'))
def check_type(link_result, expected):
    assert isinstance(link_result, Link)
    assert link_result.link_type == expected


@then(parsers.parse('the link label is "{expected}"'))
def check_label(link_result, expected):
    assert isinstance(link_result, Link)
    assert link_result.label == expected


@then("the link label is empty")
def check_label_empty(link_result):
    assert isinstance(link_result, Link)
    assert link_result.label is None


@then("a ValueError is raised")
def check_value_error(link_result):
    assert isinstance(link_result, ValueError)
