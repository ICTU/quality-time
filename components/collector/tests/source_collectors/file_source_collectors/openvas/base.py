"""Base classes for OpenVAS collector unit tests."""

from ...source_collector_test_case import SourceCollectorTestCase


class OpenVASTestCase(SourceCollectorTestCase):  # skipcq: PTC-W0046
    """Base class for OpenVAS collector unit tests."""

    SOURCE_TYPE = "openvas"
