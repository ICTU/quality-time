"""Unit tests for the Jenkins source."""

from .source_collector_test_case import SourceCollectorTestCase


class QualityTimeMetricsTest(SourceCollectorTestCase):
    """Fixture for Quality-time metrics unit tests."""

    def setUp(self):
        super().setUp()
        self.sources = dict(
            source_id=dict(
                type="quality_time", parameters=dict(url="http://quality-time/", report="r1", status=["red"])))
        self.metric = dict(type="metrics", sources=self.sources, addition="sum")

    def test_nr_of_metrics(self):
        """Test that the number of metrics is returned."""
        reports = dict(
            reports=[
                dict(
                    title="R1", report_uuid="r1", summary=dict(green=1, red=0, white=0, yellow=0, grey=0),
                    subjects=dict(subject_uuid=dict(metrics=dict(m1=dict(), m2=dict())))),
                dict(
                    title="R2", report_uuid="r2")])
        measurements = dict(measurements=[dict(metric_uuid="m1", status="green"), dict(metric_uuid="m2", status="red")])
        response = self.collect(self.metric, get_request_json_side_effect=[reports, reports, measurements, measurements])
        self.assert_value("1", response)
