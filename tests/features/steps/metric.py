"""Test the metric feature."""

from asserts import assert_equal, assert_false, assert_true
from behave import given, when, then


@given("a metric")
@when("the client creates a metric")
def add_metric(context):
    """Add a metric."""
    context.metric_uuid = context.post(f"metric/new/{context.subject_uuid}")["new_metric_uuid"]


@when("the client copies the metric")
def copy_metric(context):
    """Copy the metric."""
    context.metric_uuid = context.post(f"metric/{context.metric_uuid}/copy/{context.subject_uuid}")["new_metric_uuid"]


@when("the client moves the metric to the subject")
def move_metric(context):
    """Move the metric."""
    context.post(f"metric/{context.metric_uuid}/move/{context.subject_uuid}")


@when("the client deletes the metric")
def delete_metric(context):
    """Delete the metric."""
    context.delete(f"metric/{context.metric_uuid}")


@when('the client changes the metric {attribute} to "{value}"')
def change_metric_attribute(context, attribute, value):
    """Change the metric attribute to value."""
    context.post(f"metric/{context.metric_uuid}/attribute/{attribute}", json={attribute: value})


@then('the metric {attribute} is "{value}"')
def check_metric_attribute(context, attribute, value):
    """Check that the metric attribute equals value."""
    reports = context.get("reports")
    report = [report for report in reports["reports"] if report["report_uuid"] == context.report_uuid][0]
    assert_equal(value, report["subjects"][context.subject_uuid]["metrics"][context.metric_uuid][attribute])


@then("the metric does not exist")
def check_metric_does_not_exist(context):
    """Check that the metric does not exist."""
    reports = context.get("reports")
    report = [report for report in reports["reports"] if report["report_uuid"] == context.report_uuid][0]
    assert_false(context.metric_uuid in report["subjects"][context.subject_uuid]["metrics"])


@then("the subject contains the metric")
def check_subject_contains_metric(context):
    """Check that the subject contains the metric."""
    reports = context.get("reports")
    report = [report for report in reports["reports"] if report["report_uuid"] == context.report_uuid][0]
    assert_true(context.metric_uuid in report["subjects"][context.subject_uuid]["metrics"])
