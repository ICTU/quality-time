"""Wait step implementations."""

import time

from behave import when
from behave.runner import Context


@when("the client waits a second")
def wait(_context: Context) -> None:
    """Wait a second."""
    time.sleep(1)
