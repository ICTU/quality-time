"""Base classes the JUnit XML unit tests."""

from ...source_collector_test_case import SourceCollectorTestCase


class TestNGCollectorTestCase(SourceCollectorTestCase):
    """Base class for TestNG collector unit tests."""

    SOURCE_TYPE = "testng"
