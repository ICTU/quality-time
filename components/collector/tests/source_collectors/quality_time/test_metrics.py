"""Unit tests for the Quality-time metrics collector."""

from .base import QualityTimeTestCase


class QualityTimeMetricsTest(QualityTimeTestCase):
    """Unit tests for the Quality-time metrics collector."""

    METRIC_TYPE = "metrics"

    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.api_url = f"{self.url}/api/v3/reports"

    async def test_nr_of_metrics(self):
        """Test that the number of metrics is returned."""
        response = await self.collect(get_request_json_return_value=self.reports)
        # The count should be one because the user selected metrics from report "r1", with status "target_not_met",
        # metric type "tests" or "violations", source type "sonarqube" or "junit", and tag "security".
        # Only m2 matches those criteria.
        self.assert_measurement(
            response,
            value="1",
            total="3",
            entities=[
                dict(
                    key="m2",
                    report="R1",
                    subject="S1",
                    metric="Violations",
                    report_url=f"{self.url}/r1",
                    subject_url=f"{self.url}/r1#s1",
                    metric_url=f"{self.url}/r1#m2",
                    measurement="20 violations",
                    target="≦ 2 violations",
                    status="target_not_met",
                )
            ],
        )

    async def test_nr_of_metrics_without_reports(self):
        """Test that the number of metrics is returned."""
        self.set_source_parameter("reports", [])
        response = await self.collect(get_request_json_return_value=dict(reports=[]))
        self.assert_measurement(response, value=None, total="100", parse_error="No reports found", entities=[])

    async def test_nr_of_metrics_without_correct_report(self):
        """Test that the number of metrics is returned."""
        self.reports["reports"].pop(0)
        response = await self.collect(get_request_json_return_value=self.reports)
        self.assert_measurement(
            response, value=None, total="100", parse_error="No reports found with title or id", entities=[]
        )

    def assert_measurement(self, measurement, *, source_index: int = 0, **attributes) -> None:
        """Override to pass the api and landing URLs."""
        attributes["api_url"] = self.api_url
        super().assert_measurement(measurement, source_index=source_index, **attributes)
