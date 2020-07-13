"""Test the subject feature."""

from asserts import assert_equal
from behave import when, then


@when("the client creates a subject")
def add_subject(context):
    """Add a subject."""
    context.post(f"subject/new/{context.report_uuid}")


@then('the subject {attribute} is "{value}"')
def check_subject_attribute(context, attribute, value):
    """Check that the subject attribute equals value."""
    reports = context.get("reports")
    report = [report for report in reports["reports"] if report["report_uuid"] == context.report_uuid][0]
    print(list(report["subjects"].values())[0])
    assert_equal(value, list(report["subjects"].values())[0][attribute])
