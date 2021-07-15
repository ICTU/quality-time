"""Step implementations for tag reports."""

from asserts import assert_equal, assert_true
from behave import then, when


@when('the client gets the tag report for the tag "{tag}"')
def get_tag_report(context, tag):
    """Get the tag report for the tag."""
    context.reports = context.get(f"report/tag-{tag}")


@then("the tag report is empty")
def check_tag_report_is_empty(context):
    """Check that the tag report is empty."""
    assert_equal(0, len(context.reports["reports"]))


@then('the tag report with tag "{tag}" has only metrics with said tag')
def check_tag_report(context, tag):
    """Check that the tag report has the expected contents."""
    for subject in context.reports["reports"][0]["subjects"].values():
        for metric in subject["metrics"].values():
            assert_true(tag in metric["tags"])
