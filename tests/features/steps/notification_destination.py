"""Step implementations for notification destinations."""

from behave import given, when


@given('a notification destination')
@when('the client adds a new notification destination')
def add_not_dest(context):
    """Add a notification destination to the report."""
    report_uuid = context.uuid["report"]
    context.uuid["notification_destination"] = context.post(f"report/{report_uuid}/notification_destination/new")["new_destination_uuid"]
