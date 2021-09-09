"""Feature tests for metric specific endpoints."""
from asserts import assert_boolean_true, assert_dict_equal, assert_equal, assert_in
from behave import then


@then("the issue tracker status has '{value}' {connection} key '{key}'")
def assert_issue_tracker_status(context, value, connection, key):
    """Get the issue tracker status for this metric."""
    if value == "None":
        value = None

    tracker_status = context.get(f"metric/{context.uuid['metric']}/tracker_issue_status")

    if connection == "for":
        assert_equal(value, tracker_status[key])
    if connection == "in":
        assert_in(value, tracker_status[key])
