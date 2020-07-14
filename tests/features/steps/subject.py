"""Test the subject feature."""

from asserts import assert_equal, assert_false, assert_true
from behave import given, when, then


@given("a subject")
@when("the client creates a subject")
def add_subject(context):
    """Add a subject."""
    context.subject_uuid = context.post(f"subject/new/{context.report_uuid}")["new_subject_uuid"]


@when("the client copies the subject")
def copy_subject(context):
    """Copy the subject."""
    context.subject_uuid = context.post(f"subject/{context.subject_uuid}/copy/{context.report_uuid}")["new_subject_uuid"]


@when("the client moves the subject to the report")
def move_subject(context):
    """Move the subject."""
    context.post(f"subject/{context.subject_uuid}/move/{context.report_uuid}")


@when("the client deletes the subject")
def delete_subject(context):
    """Delete the subject."""
    context.delete(f"subject/{context.subject_uuid}")


@when('the client changes the subject {attribute} to "{value}"')
def change_subject_attribute(context, attribute, value):
    """Change the subject attribute to value."""
    context.post(f"subject/{context.subject_uuid}/attribute/{attribute}", json={attribute: value})


@then('the subject {attribute} is "{value}"')
def check_subject_attribute(context, attribute, value):
    """Check that the subject attribute equals value."""
    reports = context.get("reports")
    report = [report for report in reports["reports"] if report["report_uuid"] == context.report_uuid][0]
    assert_equal(value, report["subjects"][context.subject_uuid][attribute])


@then("the subject does not exist")
def check_subject_does_not_exist(context):
    """Check that the subject does not exist."""
    reports = context.get("reports")
    report = [report for report in reports["reports"] if report["report_uuid"] == context.report_uuid][0]
    assert_false(context.subject_uuid in report["subjects"])


@then("the report contains the subject")
def check_report_contains_subject(context):
    """Check that the report contains the subject."""
    reports = context.get("reports")
    report = [report for report in reports["reports"] if report["report_uuid"] == context.report_uuid][0]
    assert_true(context.subject_uuid in report["subjects"])
