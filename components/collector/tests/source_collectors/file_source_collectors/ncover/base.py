"""Base classes for NCover collector unit tests."""

from ...source_collector_test_case import SourceCollectorTestCase


class NCoverTestCase(SourceCollectorTestCase):  # skipcq: PTC-W0046
    """Base class for NCover collector unit tests."""

    SOURCE_TYPE = "ncover"
