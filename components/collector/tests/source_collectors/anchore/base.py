"""Unit tests for the Anchore collectors."""

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class AnchoreTestCase(SourceCollectorTestCase):
    """Base class for Anchore unit tests."""

    SOURCE_TYPE = "anchore"

    def setUp(self):
        """Extend to set up Anchore fixtures."""
        super().setUp()
        self.url = "https://cve"
        self.set_source_parameter("details_url", "image-details.json")
        self.set_source_parameter("severities", ["Low"])
        self.vulnerabilities_json = {
            "vulnerabilities": [
                {"vuln": "CVE-000", "package": "package", "fix": "None", "url": self.url, "severity": "Low"},
                {"vuln": "CVE-000", "package": "package2", "fix": "None", "url": self.url, "severity": "Unknown"},
            ],
        }
        self.details_json = [{"analyzed_at": "2020-02-07T22:53:43Z"}]
