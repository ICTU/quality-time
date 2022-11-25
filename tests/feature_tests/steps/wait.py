"""Wait step implementations."""

import time

from behave import when  # pylint: disable=no-name-in-module


@when("the client waits a second")
def wait(context):  # pylint: disable=unused-argument
    """Wait a second."""
    time.sleep(1)
