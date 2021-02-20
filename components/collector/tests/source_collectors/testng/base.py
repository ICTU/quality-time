"""Base classes the JUnit XML unit tests."""

from ..source_collector_test_case import SourceCollectorTestCase


class TestNGCollectorTestCase(SourceCollectorTestCase):  # skipcq: PTC-W0046
    """Base class for TestNG collector unit tests."""

    SOURCE_TYPE = "testng"
