"""Wait step implementations."""

import time

from behave import when


@when("the client waits a second")
def wait(context):
    """Wait a second."""
    time.sleep(1.01)
