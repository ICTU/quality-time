"""Unit tests for the Anchore collectors."""

from ...source_collector_test_case import SourceCollectorTestCase


class AnchoreTestCase(SourceCollectorTestCase):
    """Base class for Anchore unit tests."""

    SOURCE_TYPE = "anchore"

    def setUp(self):
        """Extend to set up Anchore fixtures."""
        super().setUp()
        self.url = "https://cve"
        self.sources["source_id"]["parameters"]["details_url"] = "image-details.json"
        self.sources["source_id"]["parameters"]["severities"] = ["Low"]
        self.vulnerabilities_json = dict(
            vulnerabilities=[
                dict(vuln="CVE-000", package="package", fix="None", url=self.url, severity="Low"),
                dict(vuln="CVE-000", package="package2", fix="None", url=self.url, severity="Unknown"),
            ]
        )
        self.details_json = [dict(analyzed_at="2020-02-07T22:53:43Z")]
