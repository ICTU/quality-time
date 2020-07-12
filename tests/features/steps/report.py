"""Test the report feature."""

from asserts import assert_equal, assert_true
from behave import when, then


@given("a logged-in client")
def logged_in_client(context):
    """Log in the client."""
    result = context.post("login", dict(username="admin", password="admin"))
    assert_equal(dict(ok=True, email=""), result)


@given("a report")
@when("the client creates a report")
def add_report(context):
    """Add a report."""
    context.result = context.post("report/new")
    context.report_uuid = context.result["new_report_uuids"][0]


@when("the client deletes the report")
def delete_report(context):
    """Delete the report."""
    context.result = context.delete(f"report/{context.report_uuid}")


@when('the client changes the report {attribute} to "{value}"')
def change_report_attribute(context, attribute, value):
    """Change the report attribute to value."""
    context.result = context.post(f"report/{context.report_uuid}/attribute/{attribute}", json={attribute: value})


@then('the report {attribute} is "{value}"')
def check_report_attribute(context, attribute, value):
    """Check that the report attribute equals value."""
    reports = context.get("reports")
    report = [report for report in reports["reports"] if report["report_uuid"] == context.report_uuid][0]
    assert_equal(value, report[attribute])


@then("the report does not exist")
def check_report_does_not_exist(context):
    """Check that the report does not exist."""
    reports = context.get("reports")
    assert_equal([], [report for report in reports["reports"] if report["report_uuid"] == context.report_uuid])
