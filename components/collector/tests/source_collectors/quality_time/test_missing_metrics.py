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

    def add_report_fixture(self, subject_name: str = "Subject 2"):
        """Add a report to the reports fixture."""
        self.reports["reports"].append(
            {
                "title": "Report 3",
                "report_uuid": "r3",
                "subjects": {
                    "s2": {
                        "type": "software_source_code",
                        "name": subject_name,
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

    def entities(
        self,
        subjects_to_ignore: list[str] | None = None,
        expected_subject_names: dict[str, str] | None = None,
        expected_subject_types: dict[str, str] | None = None,
    ) -> list[dict[str, str]]:
        """Create the expected entities."""
        subjects_to_ignore = subjects_to_ignore or []
        entities = []
        for report in self.reports["reports"]:
            for subject_uuid, subject in report.get("subjects", {}).items():
                if subject["name"] in subjects_to_ignore or subject_uuid in subjects_to_ignore:
                    continue
                subject_metric_types = [metric["type"] for metric in subject["metrics"].values()]
                supported_metric_types = QualityTimeMissingMetrics.supported_metric_types(self.data_model, subject)
                expected_subject_name = (expected_subject_names or {}).get(subject_uuid, subject["name"])
                expected_subject_type = (expected_subject_types or {}).get(subject_uuid, "Software")
                entities.extend(
                    [
                        self.create_entity(
                            report, subject_uuid, expected_subject_type, expected_subject_name, supported_metric_type
                        )
                        for supported_metric_type in supported_metric_types
                        if supported_metric_type not in subject_metric_types
                    ]
                )
        return entities

    def create_entity(
        self, report, subject_uuid: str, expected_subject_type: str, expected_subject_name: str, metric_type: str
    ) -> dict[str, str]:
        """Create an expected missing metric entity."""
        subject_type_name = report["subjects"][subject_uuid]["type"]
        subject_type = QualityTimeMissingMetrics.subject_type(self.data_model["subjects"], subject_type_name)
        return {
            "key": f"{report['report_uuid']}:{subject_uuid}:{metric_type}",
            "report": report["title"],
            "report_uuid": report["report_uuid"],
            "report_url": f"https://quality_time/{report['report_uuid']}",
            "subject": expected_subject_name,
            "subject_url": f"https://quality_time/{report['report_uuid']}#{subject_uuid}",
            "subject_uuid": f"{subject_uuid}",
            "subject_type": expected_subject_type,
            "subject_type_url": subject_type["reference_documentation_url"],
            "metric_type": metric_type,
            "metric_type_name": self.data_model["metrics"][metric_type]["name"],
            "metric_type_url": self.data_model["metrics"][metric_type]["reference_documentation_url"],
            "source_types": QualityTimeMissingMetrics.supporting_source_types(self.data_model, metric_type),
        }

    def assert_measurement(self, measurement, *, source_index: int = 0, **attributes: list | str | None) -> None:
        """Extend to add total."""
        attributes["total"] = str(self.nr_supported_metric_types())
        return super().assert_measurement(measurement, source_index=source_index, **attributes)

    async def test_nr_of_metrics(self):
        """Test that the number of missing metrics is returned."""
        self.add_report_fixture()
        response = await self.collect(get_request_json_side_effect=[self.data_model, self.reports])
        entities = self.entities(expected_subject_types={"s2": "Software source code"})
        self.assert_measurement(response, entities=entities, value=str(len(entities)))

    async def test_nr_of_missing_metrics_without_correct_report(self):
        """Test that an error is thrown for reports that don't exist."""
        self.add_report_fixture()
        self.set_source_parameter("reports", ["r42"])
        response = await self.collect(get_request_json_side_effect=[self.data_model, self.reports])
        self.assert_measurement(response, parse_error="No reports found with title or id")

    async def test_subjects_to_ignore_by_name(self):
        """Test that the number of non-ignored missing metrics is returned when filtered by subject name."""
        self.add_report_fixture()
        subjects_to_ignore = ["Subject2"]
        self.set_source_parameter("subjects_to_ignore", subjects_to_ignore)
        response = await self.collect(get_request_json_side_effect=[self.data_model, self.reports])
        entities = self.entities(subjects_to_ignore, expected_subject_types={"s2": "Software source code"})
        self.assert_measurement(response, entities=entities, value=str(len(entities)))

    async def test_subjects_to_ignore_by_uuid(self):
        """Test that the number of non-ignored missing metrics is returned when filtered by subject uuid."""
        self.add_report_fixture()
        subjects_to_ignore = ["s2"]
        self.set_source_parameter("subjects_to_ignore", subjects_to_ignore)
        response = await self.collect(get_request_json_side_effect=[self.data_model, self.reports])
        entities = self.entities(subjects_to_ignore, expected_subject_types={"s2": "Software source code"})
        self.assert_measurement(response, entities=entities, value=str(len(entities)))

    async def test_subjects_to_include_by_name(self):
        """Test that the number of non-ignored missing metrics is returned when filtered by subject name."""
        self.add_report_fixture()
        self.set_source_parameter("subjects_to_include", ["Subject 1"])
        response = await self.collect(get_request_json_side_effect=[self.data_model, self.reports])
        entities = self.entities(subjects_to_ignore=["Subject 2"])
        self.assert_measurement(response, entities=entities, value=str(len(entities)))

    async def test_subjects_to_include_by_uuid(self):
        """Test that the number of non-ignored missing metrics is returned when filtered by subject uuid."""
        self.add_report_fixture()
        self.set_source_parameter("subjects_to_include", ["s1"])
        response = await self.collect(get_request_json_side_effect=[self.data_model, self.reports])
        entities = self.entities(subjects_to_ignore=["Subject 2"])
        self.assert_measurement(response, entities=entities, value=str(len(entities)))

    async def test_subject_without_overridden_subject_name(self):
        """Test that the default subject name is used for subjects that don't have an overridden name."""
        self.add_report_fixture(subject_name="")
        response = await self.collect(get_request_json_side_effect=[self.data_model, self.reports])
        entities = self.entities(
            expected_subject_names={"s2": "Software source code"}, expected_subject_types={"s2": "Software source code"}
        )
        self.assert_measurement(response, entities=entities, value=str(len(entities)))

    async def test_source_types_to_include(self):
        """Test that the number of non-ignored missing metrics is returned when filtered by source type."""
        self.set_source_parameter("source_types_to_include", ["Jira"])
        response = await self.collect(get_request_json_side_effect=[self.data_model, self.reports])
        entities = [
            self.create_entity(self.reports["reports"][0], "s1", "Software", "Subject 1", metric_type)
            for metric_type in ("issues", "test_cases", "time_remaining")
        ]
        self.assert_measurement(response, entities=entities, value=str(len(entities)))

    async def test_source_types_to_ignore(self):
        """Test that the number of non-ignored missing metrics is returned when filtered by source type."""
        self.set_source_parameter(
            "source_types_to_ignore",
            QualityTimeMissingMetrics.supporting_source_types(self.data_model, "tests").split(", "),
        )
        response = await self.collect(get_request_json_side_effect=[self.data_model, self.reports])
        self.assertNotIn("tests", [entity["metric_type"] for entity in response.sources[0].entities])

    async def test_source_types_to_include_combined_with_ignored_subject(self):
        """Test that the number of non-ignored missing metrics is returned when filtered by source type and subject."""
        self.set_source_parameter("source_types_to_include", ["Jira"])
        self.set_source_parameter("subjects_to_ignore", ["s1"])
        response = await self.collect(get_request_json_side_effect=[self.data_model, self.reports])
        self.assert_measurement(response, entities=[], value="0")

    async def test_metric_types_to_ignore_when_used_at_least_once(self):
        """Test that the number of non-ignored missing metrics is returned when filtered by metric type."""
        self.add_report_fixture("Subject 2")
        # Add a second subject so the missing metrics metric reports a metric type used in the first subject,
        # but not the second
        self.reports["reports"][-1]["subjects"]["s3"] = {
            "name": "Subject 3",
            "type": "software_source_code",
            "metrics": {},
        }
        response = await self.collect(get_request_json_side_effect=[self.data_model, self.reports])
        # Check that the Size metric type is reported as missing because is is not used in both subjects
        self.assertIn("loc", [entity["metric_type"] for entity in response.sources[0].entities])
        # Now ignore metric types used at least once
        self.set_source_parameter("metric_types_to_ignore_when_used_at_least_once", ["Size (LOC)"])
        response = await self.collect(get_request_json_side_effect=[self.data_model, self.reports])
        self.assertNotIn("loc", [entity["metric_type"] for entity in response.sources[0].entities])

    async def test_metric_types_to_ignore(self):
        """Test that the number of non-ignored missing metrics is returned when filtered by metric type."""
        self.set_source_parameter("metric_types_to_ignore", ["Test results"])
        response = await self.collect(get_request_json_side_effect=[self.data_model, self.reports])
        self.assertNotIn("tests", [entity["metric_type"] for entity in response.sources[0].entities])
