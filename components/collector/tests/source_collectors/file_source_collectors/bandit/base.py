"""Base class for Bandit unit tests."""

from ...source_collector_test_case import SourceCollectorTestCase


class BanditTestCase(SourceCollectorTestCase):
    """Base class for testing Bandit collectors."""

    SOURCE_TYPE = "bandit"
