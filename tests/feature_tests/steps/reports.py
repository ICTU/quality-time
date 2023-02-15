"""Step implementations for report overviews."""

from datetime import date, timedelta

from asserts import assert_in
from behave import then, when  # pylint: disable=no-name-in-module


@when("the client gets {the_current_or_past} reports overview measurements")
def get_reports_overview_measurements(context, the_current_or_past):
    """Get the reports overview measurements."""
    if the_current_or_past == "past":
        now = date.today()
        just_now = now - timedelta(seconds=1)
        last_week = now - timedelta(days=7)
        context.report_date = just_now.isoformat()
        context.min_report_date = last_week.isoformat()
    context.get("reports_overview/measurements")


@then("the server returns the reports overview measurements")
def check_reports_overview_measurements(context):
    """Check that the response contains the measurements."""
    assert_in("measurements", context.response.json())
