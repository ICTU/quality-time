"""Unit tests for the HQ source."""

from .source_collector_test_case import SourceCollectorTestCase


class HQTest(SourceCollectorTestCase):
    """Unit tests for the HQ metrics."""

    def test_violations(self):
        """Test the number of violations."""
        hq_json = dict(metrics=[dict(stable_metric_id="id", value="10")])
        metric = dict(
            type="violations", sources=dict(a=dict(type="hq", parameters=dict(url="metrics.json", metric_id="id"))),
            addition="sum")
        response = self.collect(metric, get_request_json_return_value=hq_json)
        self.assert_measurement(response, value="10")
