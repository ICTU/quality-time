"""Unit tests for the HQ source."""

import unittest
from unittest.mock import Mock, patch

from metric_collectors import MetricCollector


class HQTest(unittest.TestCase):
    """Unit tests for the HQ metrics."""

    def test_violations(self):
        """Test the number of violations."""
        datamodel = dict(sources=dict(hq=dict(parameters=dict(metric_id=dict(default_value="")))))
        mock_response = Mock()
        mock_response.json = Mock(return_value=dict(metrics=[dict(stable_metric_id="id", value="10")]))
        metric = dict(
            type="violations", sources=dict(a=dict(type="hq", parameters=dict(url="metrics.json", metric_id="id"))),
            addition="sum")
        with patch("requests.get", return_value=mock_response):
            response = MetricCollector(metric, datamodel).get()
        self.assertEqual("10", response["sources"][0]["value"])
