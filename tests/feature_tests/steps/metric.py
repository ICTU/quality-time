"""Feature tests for metric specific attributes."""

from asserts import assert_equal, assert_true
from behave import then

from item import get_item


@then("the issue status {attribute} is '{value}'")
def assert_issue_status(context, attribute, value):
    """Get the issue status for this metric and check the attribute."""
    metric = get_item(context, "metric")
    issue_status = metric.get("issue_status")
    if value == "None":
        assert_true(None == issue_status or None == issue_status[0].get(attribute))
    else:
        assert_equal(value, issue_status[0].get(attribute))
