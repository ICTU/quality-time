"""Feature tests for metric specific attributes."""

from asserts import assert_equal
from behave import then

from item import get_item


@then("the issue status {attribute} is '{value}'")
def assert_issue_status(context, attribute, value):
    """Get the issue status for this metric and check the attribute."""
    if value == "None":
        value = None
    report = get_item(context, "report")
    print(report)
    metric = get_item(context, "metric")
    assert_equal(value, metric.get("issue_status", {}).get(attribute))
