"""Base classes for OpenVAS collector unit tests."""

from ...source_collector_test_case import SourceCollectorTestCase


class OpenVASTestCase(SourceCollectorTestCase):
    """Base class for OpenVAS collector unit tests."""

    SOURCE_TYPE = "openvas"
