"""Unit tests for the Quality-time missing metrics collector."""

import json

from shared_data_model import DATA_MODEL_JSON

from source_collectors.quality_time.missing_metrics import QualityTimeMissingMetrics

from .base import QualityTimeTestCase


class QualityTimeMissingMetricsTest(QualityTimeTestCase):
    """Unit tests for the Quality-time missing metrics collector."""

    METRIC_TYPE = "missing_metrics"

    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.data_model = json.loads(DATA_MODEL_JSON)
        self.reports["reports"].append(
            {
                "title": "R3",
                "report_uuid": "r3",
                "subjects": {
                    "s2": {
                        "type": "software_source_code",
                        "name": "Subject2",
                        "metrics": {
                            "m21": {
                                "tags": ["security"],
                                "scale": "count",
                                "type": "violations",
                                "target": "1",
                                "sources": {"s1": {"type": "sonarqube"}},
                            },
                            "m22": {
                                "tags": ["security"],
                                "scale": "count",
                                "type": "loc",
                                "target": "1",
                                "sources": {"s1": {"type": "sonarqube"}},
                            },
                        },
                    },
                },
            },
        )

    def nr_supported_metric_types(self) -> int:
        """Return the number of metric types supported by the subjects in the reports."""
        nr_supported_metrics = 0
        for report in self.reports["reports"]:
            for subject in report.get("subjects", {}).values():
                nr_supported_metrics += len(QualityTimeMissingMetrics.supported_metric_types(self.data_model, subject))
        return nr_supported_metrics

    def entities(self, subjects_to_ignore: list[str] | None = None) -> list[dict[str, str]]:
        """Create the expected entities."""
        subjects_to_ignore = subjects_to_ignore or []
        entities = []
        for report in self.reports["reports"]:
            for subject_uuid, subject in report.get("subjects", {}).items():
                if subject["name"] in subjects_to_ignore or subject_uuid in subjects_to_ignore:
                    continue
                subject_metric_types = [metric["type"] for metric in subject["metrics"].values()]
                supported_metric_types = QualityTimeMissingMetrics.supported_metric_types(self.data_model, subject)
                entities.extend(
                    [
                        self.create_entity(report, subject_uuid, subject, supported_metric_type)
                        for supported_metric_type in supported_metric_types
                        if supported_metric_type not in subject_metric_types
                    ]
                )
        return entities

    def create_entity(self, report, subject_uuid: str, subject, metric_type: str) -> dict[str, str]:
        """Create a missing metric entity."""
        data_model_subject = QualityTimeMissingMetrics.subject_type(self.data_model["subjects"], subject["type"])
        return {
            "key": f"{report['report_uuid']}:{subject_uuid}:{metric_type}",
            "report": report["title"],
            "report_url": f"https://quality_time/{report['report_uuid']}",
            "subject": subject["name"],
            "subject_url": f"https://quality_time/{report['report_uuid']}#{subject_uuid}",
            "subject_uuid": f"{subject_uuid}",
            "subject_type": data_model_subject["name"] if data_model_subject else "missing",
            "metric_type": self.data_model["metrics"][metric_type]["name"],
        }

    async def test_nr_of_metrics(self):
        """Test that the number of missing metrics is returned."""
        response = await self.collect(get_request_json_side_effect=[self.data_model, self.reports])
        entities = self.entities()
        self.assert_measurement(
            response,
            entities=entities,
            total=str(self.nr_supported_metric_types()),
            value=str(len(entities)),
        )

    async def test_nr_of_missing_metrics_without_correct_report(self):
        """Test that an error is thrown for reports that don't exist."""
        self.set_source_parameter("reports", ["r42"])
        response = await self.collect(get_request_json_side_effect=[self.data_model, self.reports])
        self.assert_measurement(response, parse_error="No reports found with title or id")

    async def test_subjects_to_ignore_by_name(self):
        """Test that the number of non-ignored missing metrics is returned when filtered by name."""
        subjects_to_ignore = ["Subject2"]
        self.set_source_parameter("subjects_to_ignore", subjects_to_ignore)
        response = await self.collect(get_request_json_side_effect=[self.data_model, self.reports])
        entities = self.entities(subjects_to_ignore)
        self.assert_measurement(
            response,
            entities=entities,
            total=str(self.nr_supported_metric_types()),
            value=str(len(entities)),
        )

    async def test_subjects_to_ignore_by_uuid(self):
        """Test that the number of non-ignored missing metrics is returned when filtered by uuid."""
        subjects_to_ignore = ["s2"]
        self.set_source_parameter("subjects_to_ignore", subjects_to_ignore)
        response = await self.collect(get_request_json_side_effect=[self.data_model, self.reports])
        entities = self.entities(subjects_to_ignore)
        self.assert_measurement(
            response,
            entities=entities,
            total=str(self.nr_supported_metric_types()),
            value=str(len(entities)),
        )
