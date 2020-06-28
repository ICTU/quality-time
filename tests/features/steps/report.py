"""Test the report feature."""

from asserts import assert_equal
from behave import when, then

import requests


@given("a logged-in client")
def logged_in_client(context):
    """Log in the client."""
    result = context.post("login", dict(username="admin", password="admin"))
    assert_equal(dict(ok=True, email=""), result)


@when("the client creates a new report")
def add_report(context):
    """Add a report."""
    context.result = context.post("report/new")


@then("the server returns OK")
def check_answer(context):
    """Check the answer."""
    assert_equal(dict(ok=True), context.result)
