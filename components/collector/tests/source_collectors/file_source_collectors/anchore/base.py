"""Unit tests for the Anchore collectors."""

from ...source_collector_test_case import SourceCollectorTestCase


class AnchoreTestCase(SourceCollectorTestCase):
    """Base class for Anchore unit tests."""

    METRIC_TYPE = "Subclass responsibility"
    METRIC_ADDITION = "sum"

    def setUp(self):
        """Extend to set up Anchore fixtures."""
        super().setUp()
        self.url = "https://cve"
        self.sources = dict(
            source_id=dict(
                type="anchore",
                parameters=dict(url="image-vuln.json", details_url="image-details.json", severities=["Low"]),
            )
        )
        self.metric = dict(type=self.METRIC_TYPE, sources=self.sources, addition=self.METRIC_ADDITION)
        self.vulnerabilities_json = dict(
            vulnerabilities=[
                dict(vuln="CVE-000", package="package", fix="None", url=self.url, severity="Low"),
                dict(vuln="CVE-000", package="package2", fix="None", url=self.url, severity="Unknown"),
            ]
        )
        self.details_json = [dict(analyzed_at="2020-02-07T22:53:43Z")]
