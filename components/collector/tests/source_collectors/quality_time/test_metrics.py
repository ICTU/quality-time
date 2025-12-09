"""Unit tests for the Quality-time metrics collector."""

from shared.utils.date_time import now

from .base import QualityTimeTestCase


class QualityTimeMetricsTest(QualityTimeTestCase):
    """Unit tests for the Quality-time metrics collector."""

    METRIC_TYPE = "metrics"

    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.entities = [
            {
                "key": "m2",
                "report": "Report 1",
                "subject": "Subject 1",
                "metric": "Violations",
                "report_url": f"{self.url}/r1",
                "subject_url": f"{self.url}/r1#s1",
                "metric_url": f"{self.url}/r1#m2",
                "measurement": "20",
                "target": "≦ 2",
                "unit": "violations",
                "status": "target_not_met",
                "status_start_date": "2020-05-23T07:53:17+00:00",
            },
        ]

    def assert_measurement(self, measurement, *, source_index: int = 0, **attributes: list | str | None) -> None:
        """Override to pass the api and landing URLs."""
        attributes["api_url"] = f"{self.url}/api/internal/report"
        super().assert_measurement(measurement, source_index=source_index, **attributes)

    async def test_nr_of_metrics(self):
        """Test that the number of metrics is returned."""
        self.set_source_parameter("metric_type", ["Test results", "Violations"])
        self.set_source_parameter("source_type", ["SonarQube"])
        self.set_source_parameter("tags", ["security"])
        self.set_source_parameter("status", ["target not met (red)"])
        response = await self.collect(get_request_json_return_value=self.reports)
        # The count should be one because the user selected metrics from report "r1", with status "target_not_met",
        # metric type "tests" or "violations", source type "sonarqube" or "junit", and tag "security".
        # Only m2 matches those criteria.
        self.assert_measurement(response, value="1", total="3", entities=self.entities)

    async def test_nr_of_metrics_without_reports(self):
        """Test that an error is thrown if no reports exist."""
        response = await self.collect(get_request_json_return_value={"reports": []})
        self.assert_measurement(response, parse_error="No reports found")

    async def test_nr_of_metrics_without_correct_report(self):
        """Test that an error is thrown for reports that don't exist."""
        self.set_source_parameter("reports", ["r42"])
        response = await self.collect(get_request_json_return_value=self.reports)
        self.assert_measurement(response, parse_error="No reports found with title or id")

    async def test_nr_of_metrics_with_min_status_duration(self):
        """Test that metrics with a recently changed status are ignored."""
        self.set_source_parameter("metric_type", ["Test results", "Violations"])
        self.set_source_parameter("source_type", ["SonarQube"])
        self.set_source_parameter("tags", ["security"])
        self.set_source_parameter("status", ["target not met (red)", "target met (green)"])
        self.set_source_parameter("min_status_duration", "5")
        metrics = self.reports["reports"][0]["subjects"]["s1"]["metrics"]
        # Give m1 a recently changed status to test that it will be ignored
        metrics["m1"]["status_start"] = now().isoformat()
        # Give m3 a status but no change date to test that it will be ignored
        metrics["m3"]["recent_measurements"].append({"count": {"status": "target_met"}})
        response = await self.collect(get_request_json_return_value=self.reports)
        self.assert_measurement(response, value="1", total="3", entities=self.entities)
