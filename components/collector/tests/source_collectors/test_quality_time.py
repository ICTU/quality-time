"""Unit tests for the Quality-time source collector(s)."""

from .source_collector_test_case import SourceCollectorTestCase


class QualityTimeMetricsTest(SourceCollectorTestCase):
    """Fixture for Quality-time metrics unit tests."""

    def test_nr_of_metrics(self):
        """Test that the number of metrics is returned."""
        sources = dict(
            source_id=dict(
                type="quality_time",
                parameters=dict(
                    url="https://quality-time/", reports=["r1"], status=["target not met (red)"], tags=["security"],
                    metric_type=["tests", "violations"], source_type=["sonarqube"])))
        metric = dict(type="metrics", sources=sources, addition="sum")
        reports = dict(
            reports=[
                dict(
                    title="R1", report_uuid="r1",
                    subjects=dict(
                        s1=dict(
                            name="S1",
                            metrics=dict(
                                m1=dict(
                                    tags=["security"], scale="count", type="violations", report_uuid="r1", target="1",
                                    sources=dict(s1=dict(type="sonarqube"))),
                                m2=dict(
                                    tags=["security"], scale="count", type="violations", report_uuid="r1", target="2",
                                    sources=dict(s2=dict(type="sonarqube"))),
                                m3=dict(
                                    tags=["security"], scale="count", type="violations", report_uuid="r1", target="3",
                                    sources=dict(s3=dict(type="sonarqube"))),
                                m4=dict(
                                    tags=["security"], scale="count", type="violations", report_uuid="r1", target="4",
                                    sources=dict(s4=dict(type="junit"))),
                                m5=dict(
                                    tags=["performance"], scale="count", type="violations", report_uuid="r1",
                                    target="5", sources=dict(s5=dict(type="sonarqube"))),
                                m6=dict(
                                    tags=["security"], scale="count", type="loc", report_uuid="r1", target="6",
                                    sources=dict(s6=dict(type="sonarqube"))))))),
                dict(
                    title="R2", report_uuid="r2")])
        measurements1 = dict(measurements=[dict(metric_uuid="m1", count=dict(status="target_met", value="0"))])
        measurements2 = dict(measurements=[dict(metric_uuid="m2", count=dict(status="target_not_met", value="20"))])
        measurements3 = dict(measurements=[])
        response = self.collect(
            metric, get_request_json_side_effect=[reports, measurements1, measurements2, measurements3])
        # The count should be one because the user selected metrics from report "r1", with status "target_not_met",
        # metric type "tests" or "violations", source type "sonarqube" or "junit", and tag "security".
        # Only m2 matches those criteria.
        self.assert_measurement(
            response, value="1", total="3", api_url="https://quality-time/api/v1", landing_url="https://quality-time",
            entities=[
                dict(
                    key="m2", report="R1", subject="S1", metric="Violations", report_url="https://quality-time/r1",
                    subject_url="https://quality-time/r1#s1", metric_url="https://quality-time/r1#m2",
                    measurement="20 violations", target="≦ 2 violations", status="target_not_met")])
