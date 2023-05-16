"""Base classes for Quality-time collector unit tests."""

from ..source_collector_test_case import SourceCollectorTestCase


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
        self.reports = dict(
            reports=[
                dict(
                    title="R1",
                    report_uuid="r1",
                    subjects=dict(
                        s1=dict(
                            type="software",
                            name="S1",
                            metrics=dict(
                                m1=dict(
                                    tags=["security"],
                                    scale="count",
                                    type="violations",
                                    target="1",
                                    sources=dict(s1=dict(type="sonarqube")),
                                    recent_measurements=[
                                        dict(
                                            count=dict(status="target_not_met", value="10"),
                                            end="2020-06-23T07:53:17+00:00",
                                        ),
                                        dict(
                                            count=dict(status="target_met", value="0"), end="2020-06-24T07:53:17+00:00"
                                        ),
                                    ],
                                ),
                                m2=dict(
                                    tags=["security"],
                                    scale="count",
                                    type="violations",
                                    target="2",
                                    status_start="2020-05-23T07:53:17+00:00",
                                    sources=dict(s2=dict(type="sonarqube")),
                                    recent_measurements=[
                                        dict(
                                            count=dict(status="target_not_met", value="20"),
                                            end="2020-06-25T07:53:17+00:00",
                                        )
                                    ],
                                ),
                                m3=dict(
                                    tags=["security"],
                                    scale="count",
                                    type="violations",
                                    target="3",
                                    recent_measurements=[],
                                    sources=dict(s3=dict(type="sonarqube")),
                                ),
                                m4=dict(
                                    tags=["security"],
                                    scale="count",
                                    type="violations",
                                    target="4",
                                    sources=dict(s4=dict(type="junit")),
                                ),
                                m5=dict(
                                    tags=["performance"],
                                    scale="count",
                                    type="accessibility",
                                    target="5",
                                    sources=dict(s5=dict(type="sonarqube")),
                                ),
                                m6=dict(
                                    tags=["security"],
                                    scale="count",
                                    type="loc",
                                    target="6",
                                    sources=dict(s6=dict(type="sonarqube")),
                                ),
                            ),
                        )
                    ),
                ),
                dict(title="R2", report_uuid="r2"),
            ]
        )

    def assert_measurement(self, measurement, *, source_index: int = 0, **attributes) -> None:
        """Override to pass the api and landing URLs."""
        attributes["landing_url"] = self.url
        super().assert_measurement(measurement, source_index=source_index, **attributes)
