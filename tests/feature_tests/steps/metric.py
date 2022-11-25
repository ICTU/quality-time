"""Feature tests for metric specific attributes."""

from asserts import assert_equal, assert_false, assert_true
from behave import then, when  # pylint: disable=no-name-in-module

from item import get_item


@then("the issue status {attribute} is '{value}'")
def assert_issue_status(context, attribute, value):
    """Get the issue status for this metric and check the attribute."""
    metric = get_item(context, "metric")
    issue_status = metric.get("issue_status")
    if value == "None":
        assert_true(None is issue_status or None is issue_status[0].get(attribute))
    else:
        assert_equal(value, issue_status[0].get(attribute))


@then("the issue id suggestions are missing")
def assert_issue_id_suggestions(context):
    """Check the issue id suggestions."""
    suggestions = context.get(f"report/{context.uuid['report']}/issue_tracker/suggestions/random_query")
    assert_equal(dict(suggestions=[]), suggestions)


@when("the client retrieves the issue tracker options")
def retrieve_issue_tracker_options(context):
    """Get the issue tracker options."""
    context.response = context.get(f"report/{context.uuid['report']}/issue_tracker/options")


@then("the issue tracker options are missing")
def assert_issue_tracker_options(context):
    """Check the issue tracker options."""
    assert_equal(dict(fields=[], issue_types=[], projects=[], epic_links=[]), context.response)


@when("the client opens a new issue")
def create_new_issue(context):
    """Create a new issue for the current metric."""
    context.post(f"metric/{context.uuid['metric']}/issue/new", dict(metric_url="https://metric"))


@then("the new issue response error is '{error}'")
def new_issue_response(context, error):
    """Check the new issue response."""
    json = context.response.json()
    assert_false(json["ok"])
    assert_true(error in json["error"])
