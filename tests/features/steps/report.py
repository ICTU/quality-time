"""Test the report feature."""

from asserts import assert_equal, assert_true
from behave import when, then


@given("a logged-in client")
def logged_in_client(context):
    """Log in the client."""
    result = context.post("login", dict(username="admin", password="admin"))
    assert_equal(dict(ok=True, email=""), result)


@when("the client creates a new report")
def add_report(context):
    """Add a report."""
    context.result = context.post("report/new")
    context.report_uuid = context.result["new_report_uuids"][0]


@when("the client deletes the new report")
def delete_report(context):
    """Delete the new report."""
    import time
    time.sleep(0.5)
    context.result = context.delete(f"report/{context.report_uuid}")


@then("the server returns OK")
def check_answer(context):
    """Check the answer."""
    assert_true(context.result["ok"])
