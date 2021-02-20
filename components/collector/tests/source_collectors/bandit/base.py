"""Base class for Bandit unit tests."""

from ..source_collector_test_case import SourceCollectorTestCase


class BanditTestCase(SourceCollectorTestCase):  # skipcq: PTC-W0046
    """Base class for testing Bandit collectors."""

    SOURCE_TYPE = "bandit"
