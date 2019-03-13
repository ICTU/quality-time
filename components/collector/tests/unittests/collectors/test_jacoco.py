"""Unit tests for the JaCoCo source."""

import unittest
from unittest.mock import Mock, patch

from collector.collector import Collector, collect_measurement


class JaCoCoTest(unittest.TestCase):
    """Unit tests for the JaCoCo metrics."""

    def setUp(self):
        """Test fixture."""
        Collector.RESPONSE_CACHE.clear()
        self.mock_response = Mock()
        self.sources = dict(source_id=dict(type="jacoco", parameters=dict(url="http://jacoco/")))

    def test_uncovered_lines(self):
        """Test that the number of uncovered lines is returned."""
        self.mock_response.text = "<report><counter type='LINE' missed='2' /></report>"
        metric = dict(type="uncovered_lines", sources=self.sources)
        with patch("requests.get", return_value=self.mock_response):
            response = collect_measurement(metric)
        self.assertEqual("2", response["sources"][0]["value"])

    def test_uncovered_branches(self):
        """Test that the number of uncovered branches is returned."""
        self.mock_response.text = "<report><counter type='BRANCH' missed='4' /></report>"
        metric = dict(type="uncovered_branches", sources=self.sources)
        with patch("requests.get", return_value=self.mock_response):
            response = collect_measurement(metric)
        self.assertEqual("4", response["sources"][0]["value"])
