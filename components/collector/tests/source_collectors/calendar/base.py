"""Base class for calendar collector unit tests."""

from ..source_collector_test_case import SourceCollectorTestCase


class CalendarTestCase(SourceCollectorTestCase):  # skipcq: PTC-W0046
    """Base class for calendar collectors."""

    SOURCE_TYPE = "calendar"
