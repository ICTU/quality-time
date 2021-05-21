"""Unit tests for the Quality-time missing metrics collector."""

from .base import QualityTimeTestCase


class QualityTimeMissingMetricsTest(QualityTimeTestCase):
    """Unit tests for the Quality-time missing metrics collector."""

    METRIC_TYPE = "missing_metrics"

    async def test_nr_of_metrics(self):
        """Test that the number of missing_metrics is returned."""
        response = await self.collect(get_request_json_side_effect=[self.data_model, self.reports])
        entities = [
            dict(
                key=metric_type,
                metric_type=metric_type,
                reports=["R1"],
                subject_type="S1",
            )
            for metric_type in self.data_model["subjects"]["software"]["metrics"]
            if metric_type not in ["violations", "accessibility", "loc"]
        ]
        self.assert_measurement(
            response,
            value=str(len(entities)),
            entities=entities,
        )

    async def test_nr_of_missing_metrics_without_reports(self):
        """Test that the number of metrics is returned."""
        self.set_source_parameter("reports", [])
        response = await self.collect(get_request_json_return_value=dict(reports=[]))
        self.assert_measurement(response, value=None, parse_error="No reports found", entities=[])

    async def test_nr_of_missing_metrics_without_correct_report(self):
        """Test that the number of metrics is returned."""
        self.reports["reports"].pop(0)
        response = await self.collect(get_request_json_return_value=self.reports)
        self.assert_measurement(response, value=None, parse_error="No reports found with title or id", entities=[])
