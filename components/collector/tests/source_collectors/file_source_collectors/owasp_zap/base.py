"""Base classes for OWASP ZAP collector unit tests."""

from ...source_collector_test_case import SourceCollectorTestCase


class OWASPZAPTestCase(SourceCollectorTestCase):  # skipcq: PTC-W0046
    """Base class for OpenVAS collector unit tests."""

    SOURCE_TYPE = "owasp_zap"
