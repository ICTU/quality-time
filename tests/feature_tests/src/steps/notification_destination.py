"""Step implementations for notification destinations."""

from behave import given, when
from behave.runner import Context


@given("a notification destination")
@when("the client adds a new notification destination")
def add_notification_destination(context: Context) -> None:
    """Add a notification destination to the report."""
    api = f"report/{context.uuid['report']}/notification_destination/new"
    context.uuid["notification_destination"] = context.post(api)["new_destination_uuid"]


@when("the client adds a notification destination to a non-existing report")
def add_notification_destination_to_non_existing_report(context: Context) -> None:
    """Add a notification destination to a non-existing report."""
    context.uuid["report"] = report_uuid = "report-does-not-exist"
    context.post(f"report/{report_uuid}/notification_destination/new")


@when("the client deletes a notification destination of a non-existing report")
def delete_notification_destination_of_non_existing_report(context: Context) -> None:
    """Delete a notification destination of a non-existing report."""
    context.uuid["report"] = report_uuid = "report-does-not-exist"
    context.delete(f"report/{report_uuid}/notification_destination/notification_destination_uuid")


@when("the client changes a notification_destination name of a non-existing report")
def change_notification_destination_of_non_existing_report(context: Context) -> None:
    """Change the notification destination of a non-existing report."""
    context.uuid["report"] = report_uuid = "report-does-not-exist"
    context.post(
        f"report/{report_uuid}/notification_destination/notification_destionation_uuid/attributes",
        json={"name": "New name"},
    )
