"""Step implementations for notifications."""

from asserts import assert_equal
from behave import then, when  # pylint: disable=no-name-in-module


@when("the notifier gets the notification data")
def get_notification_data(context):
    """Get the notification data."""
    context.get("measurements", internal=True)


@then("the internal server returns two measurements for the metric")
def check_internal_server_measurements(context):
    """Check that the response contains the measurements."""
    measurements = context.response.json()["measurements"]
    assert_equal(2, len([m for m in measurements if m["metric_uuid"] == context.uuid["metric"]]))
