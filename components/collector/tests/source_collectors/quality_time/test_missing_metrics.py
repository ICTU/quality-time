"""Unit tests for the Quality-time missing metrics collector."""

from .base import QualityTimeTestCase


class QualityTimeMissingMetricsTest(QualityTimeTestCase):
    """Unit tests for the Quality-time missing metrics collector."""

    METRIC_TYPE = "missing_metrics"

    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.set_source_parameter("reports", ["r1", "r3"])
        self.expected_software_metrics = str(2 * len(self.data_model["subjects"]["software"]["metrics"]))
        self.reports["reports"].append(
            dict(
                title="R3",
                report_uuid="r3",
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
        self.entities = []
        for report in self.reports["reports"]:
            for subject_uuid, subject in report.get("subjects", {}).items():
                for metric_type in self.data_model["subjects"]["software"]["metrics"]:
                    if metric_type not in ["violations", "accessibility", "loc"]:
                        self.entities.append(
                            dict(
                                key=f"{report['report_uuid']}:{subject_uuid}:{metric_type}",
                                report=report["title"],
                                report_url=f"https://quality_time/{report['report_uuid']}",
                                subject=subject["name"],
                                subject_url=f"https://quality_time/{report['report_uuid']}#{subject_uuid}",
                                subject_type=self.data_model["subjects"][subject["type"]]["name"],
                                metric_type=self.data_model["metrics"][metric_type]["name"],
                            )
                        )

    async def test_nr_of_metrics(self):
        """Test that the number of missing metrics is returned."""
        response = await self.collect(get_request_json_side_effect=[self.data_model, self.reports])
        self.assert_measurement(
            response, value=str(len(self.entities)), total=self.expected_software_metrics, entities=self.entities
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
        self.assert_measurement(response, parse_error="No reports found with title or id")
