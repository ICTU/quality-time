"""Wait step implementations."""

import time
from typing import TYPE_CHECKING

from behave import when

if TYPE_CHECKING:
    from behave.runner import Context


@when("the client waits a second")
def wait(_context: Context) -> None:
    """Wait a second."""
    time.sleep(1)
