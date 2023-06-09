"""Step implementations for notification destinations."""

from behave import given, when
from behave.runner import Context


@given("a notification destination")
@when("the client adds a new notification destination")
def add_notification_destination(context: Context) -> None:
    """Add a notification destination to the report."""
    api = f"report/{context.uuid['report']}/notification_destination/new"
    context.uuid["notification_destination"] = context.post(api)["new_destination_uuid"]
