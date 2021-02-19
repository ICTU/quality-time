"""Base classes for OWASP ZAP collector unit tests."""

from ...source_collector_test_case import SourceCollectorTestCase


class OWASPZAPTestCase(SourceCollectorTestCase):
    """Base class for OpenVAS collector unit tests."""

    SOURCE_TYPE = "owasp_zap"
