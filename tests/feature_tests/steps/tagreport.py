"""Step implementations for tag reports."""

from asserts import assert_equal, assert_true


@when('the client gets the tag report for the tag "{tag}"')
def get_tag_report(context, tag):
    """Get the tag report for the tag."""
    context.tag_report = context.get(f"tagreport/{tag}")


@then("the tag report is empty")
def check_tag_report_is_empty(context):
    """Check that the tag report is empty."""
    assert_equal({}, context.tag_report["subjects"])


@then('the tag report with tag "{tag}" has only metrics with said tag')
def check_tag_report(context, tag):
    """Check that the tag report has the expected contents."""
    for subject in context.tag_report["subjects"].values():
        for metric in subject["metrics"].values():
            assert_true(tag in metric["tags"])
