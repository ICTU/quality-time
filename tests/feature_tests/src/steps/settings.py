"""Steps for settings."""

import json

from asserts import assert_equal, assert_true
from behave import then, when
from behave.runner import Context


@when("the client posts new settings")
def post_settings(context: Context) -> None:
    """Post new settings."""
    context.put("settings", json=json.loads(context.text))


@then("the settings have been updated")
def check_post_settings(context: Context) -> None:
    """Check that the server responded with ok."""
    assert_true(200, context.response.status_code)


@when("the client retrieves settings")
def get_settings(context: Context) -> None:
    """Get settings."""
    context.get("settings")


@then("the settings are returned")
def check_get_settings(context: Context) -> None:
    """Check that the settings are returned."""
    settings = context.response.json()["settings"]
    assert_equal(settings, json.loads(context.text))
