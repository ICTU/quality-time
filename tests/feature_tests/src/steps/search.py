"""Search step implementations for reports, subjects, metrics, and sources."""

from typing import TYPE_CHECKING

from asserts import assert_equal, assert_false, assert_in, assert_true
from behave import then, when

if TYPE_CHECKING:
    from behave.runner import Context


@when('the client searches a {domain_object_type} with {attribute_name} "{attribute_value}"')
def search(context: Context, domain_object_type: str, attribute_name: str, attribute_value: str) -> None:
    """Search for domain objects of the specified type with the specified attribute."""
    with context.external_api():
        context.post(f"{domain_object_type}/search", json={attribute_name: attribute_value})


@when("the client searches a report without query parameters")
def search_invalid(context: Context) -> None:
    """Search with invalid query parameters."""
    with context.external_api():
        context.post("report/search", json={})


@then("the search results contain the uuid of the {domain_object_type}")
def check_search_results(context: Context, domain_object_type: str) -> None:
    """Check the search results."""
    assert_in(context.uuid[domain_object_type], context.response.json()["uuids"])


@then("the search results are empty")
def check_no_search_results(context: Context) -> None:
    """Check that the search results are empty."""
    results = context.response.json()
    assert_true(results["ok"])
    assert_equal([], results["uuids"])


@then("the search results contain an error message")
def check_invalid_search(context: Context) -> None:
    """Check that the search result is an error message."""
    assert_false(context.response.json()["ok"])
