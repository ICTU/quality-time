"""Unit tests for the Quality-time missing metrics collector."""

from .base import QualityTimeTestCase


class QualityTimeMissingMetricsTest(QualityTimeTestCase):
    """Unit tests for the Quality-time missing metrics collector."""

    METRIC_TYPE = "missing_metrics"

    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.set_source_parameter("reports", ["r1", "r2"])
        self.expected_software_metrics = str(len(self.data_model["subjects"]["software"]["metrics"]))
        self.reports["reports"].append(
            dict(
                title="R2",
                report_uuid="r2",
                subjects=dict(
                    s2=dict(
                        type="software",
                        name="S2",
                        metrics=dict(
                            m21=dict(
                                tags=["security"],
                                scale="count",
                                type="violations",
                                target="1",
                                sources=dict(s1=dict(type="sonarqube")),
                            ),
                            m22=dict(
                                tags=["security"],
                                scale="count",
                                type="loc",
                                target="1",
                                sources=dict(s1=dict(type="sonarqube")),
                            ),
                            m23=dict(
                                tags=["security"],
                                scale="count",
                                type="accessibility",
                                target="1",
                                sources=dict(s1=dict(type="sonarqube")),
                            ),
                        ),
                    )
                ),
            ),
        )

        self.entities = [
            dict(
                key=metric_type,
                metric_type=metric_type,
                reports=["R1", "R2"],
                subject_type="S1",
            )
            for metric_type in self.data_model["subjects"]["software"]["metrics"]
            if metric_type not in ["violations", "accessibility", "loc"]
        ]

    async def test_nr_of_metrics(self):
        """Test that the number of missing_metrics is returned."""
        response = await self.collect(get_request_json_side_effect=[self.data_model, self.reports])
        self.assert_measurement(
            response,
            value=str(len(self.entities)),
            total=self.expected_software_metrics,
            entities=self.entities,
        )

    async def test_nr_of_missing_metrics_without_reports(self):
        """Test that no reports in the parameter equals all reports."""
        self.set_source_parameter("reports", [])
        response = await self.collect(get_request_json_side_effect=[self.data_model, self.reports])
        self.assert_measurement(
            response, value=str(len(self.entities)), total=self.expected_software_metrics, entities=self.entities
        )

    async def test_nr_of_missing_metrics_without_correct_report(self):
        """Test that an error is thrown for reports that don't exist."""
        self.reports["reports"] = []
        response = await self.collect(get_request_json_side_effect=[self.data_model, self.reports])
        self.assert_measurement(response, value=None, parse_error="No reports found with title or id", entities=[])
