"""Base classes for Quality-time collector unit tests."""

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class QualityTimeTestCase(SourceCollectorTestCase):
    """Base class for Quality-time collector unit tests."""

    SOURCE_TYPE = "quality_time"

    def setUp(self):
        """Extend to set up fixtures for Quality-time metrics unit tests."""
        super().setUp()
        self.url = "https://quality_time"
        self.set_source_parameter("reports", ["r1"])
        self.set_source_parameter("status", ["target not met (red)"])
        self.set_source_parameter("tags", ["security"])
        self.set_source_parameter("metric_type", ["Tests", "Violations"])
        self.set_source_parameter("source_type", ["SonarQube"])
        self.reports = {
            "reports": [
                {
                    "title": "R1",
                    "report_uuid": "r1",
                    "subjects": {
                        "s1": {
                            "type": "software",
                            "name": "S1",
                            "metrics": {
                                "m1": {
                                    "tags": ["security"],
                                    "scale": "count",
                                    "type": "violations",
                                    "target": "1",
                                    "sources": {"s1": {"type": "sonarqube"}},
                                    "recent_measurements": [
                                        {
                                            "count": {"status": "target_not_met", "value": "10"},
                                            "end": "2020-06-23T07:53:17+00:00",
                                        },
                                        {
                                            "count": {"status": "target_met", "value": "0"},
                                            "end": "2020-06-24T07:53:17+00:00",
                                        },
                                    ],
                                },
                                "m2": {
                                    "tags": ["security"],
                                    "scale": "count",
                                    "type": "violations",
                                    "target": "2",
                                    "status_start": "2020-05-23T07:53:17+00:00",
                                    "sources": {"s2": {"type": "sonarqube"}},
                                    "recent_measurements": [
                                        {
                                            "count": {"status": "target_not_met", "value": "20"},
                                            "end": "2020-06-25T07:53:17+00:00",
                                        },
                                    ],
                                },
                                "m3": {
                                    "tags": ["security"],
                                    "scale": "count",
                                    "type": "violations",
                                    "target": "3",
                                    "recent_measurements": [],
                                    "sources": {"s3": {"type": "sonarqube"}},
                                },
                                "m4": {
                                    "tags": ["security"],
                                    "scale": "count",
                                    "type": "violations",
                                    "target": "4",
                                    "sources": {"s4": {"type": "junit"}},
                                },
                                "m5": {
                                    "tags": ["performance"],
                                    "scale": "count",
                                    "type": "accessibility",
                                    "target": "5",
                                    "sources": {"s5": {"type": "sonarqube"}},
                                },
                                "m6": {
                                    "tags": ["security"],
                                    "scale": "count",
                                    "type": "loc",
                                    "target": "6",
                                    "sources": {"s6": {"type": "sonarqube"}},
                                },
                            },
                        },
                    },
                },
                {"title": "R2", "report_uuid": "r2"},
            ],
        }

    def assert_measurement(self, measurement, *, source_index: int = 0, **attributes: list | str | None) -> None:
        """Override to pass the api and landing URLs."""
        attributes["landing_url"] = self.url
        super().assert_measurement(measurement, source_index=source_index, **attributes)
