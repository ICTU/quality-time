"""Step implementations for notification destinations."""

from asserts import assert_equal
from behave import given, then, when
from behave.runner import Context


@given("a notification destination")
@when("the client adds a new notification destination")
def add_notification_destination(context: Context) -> None:
    """Add a notification destination to the report."""
    api = f"report/{context.uuid['report']}/notification_destination/new"
    context.uuid["notification_destination"] = context.post(api)["new_destination_uuid"]


@then("the internal report endpoint has the new notification destination")
def get_notification_destionation(context: Context) -> None:
    """Get the notification destination from the internal report endpoint."""
    reports = context.get("report", internal=True)
    report = [report for report in reports["reports"] if report["report_uuid"] == context.uuid["report"]][0]
    assert_equal(
        {"webhook": "", "name": "Microsoft Teams webhook", "sleep_duration": 0},
        report["notification_destinations"][context.uuid["notification_destination"]],
    )
