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
                    url="https://quality-time/", reports=["r1"], status=["target not met (red)"], tags=["security"])))
        metric = dict(type="metrics", sources=sources, addition="sum")
        reports = dict(
            reports=[
                dict(
                    title="R1", report_uuid="r1",
                    subjects=dict(
                        subject_uuid=dict(
                            metrics=dict(
                                m1=dict(tags=["security"]), m2=dict(tags=["security"]), m3=dict(tags=["security"]),
                                m4=dict())))),
                dict(
                    title="R2", report_uuid="r2")])
        measurements1 = dict(measurements=[dict(metric_uuid="m1", status="target_met")])
        measurements2 = dict(measurements=[dict(metric_uuid="m2", status="target_not_met")])
        measurements3 = dict(measurements=[])
        response = self.collect(
            metric, get_request_json_side_effect=[reports, measurements1, measurements2, measurements3, reports])
        # The count should be one because the user selected metrics from report "r1", with status "target_not_met",
        # and tag "security". Only m2 matches those criteria.
        self.assert_value("1", response)

    def test_metric_percentage(self):
        """Test that the total number of metrics is returned if the metric scale is percentage."""
        sources = dict(
            source_id=dict(
                type="quality_time",
                parameters=dict(
                    url="http://quality-time/", reports=["r1"], status=["target not met (red)"], tags=["security"])))
        metric = dict(type="metrics", sources=sources, addition="sum", scale="percentage")
        reports = dict(
            reports=[
                dict(
                    title="R1", report_uuid="r1",
                    subjects=dict(
                        subject_uuid=dict(
                            metrics=dict(
                                m1=dict(tags=["security"]), m2=dict(tags=["security"]), m3=dict(tags=["security"]),
                                m4=dict())))),
                dict(
                    title="R2", report_uuid="r2")])
        measurements1 = dict(measurements=[dict(metric_uuid="m1", status="target_met")])
        measurements2 = dict(measurements=[dict(metric_uuid="m2", status="target_not_met")])
        measurements3 = dict(measurements=[])
        response = self.collect(
            metric, get_request_json_side_effect=[reports, measurements1, measurements2, measurements3, reports, reports])
        self.assert_total("3", response)
