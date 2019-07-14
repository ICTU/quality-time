"""Unit tests for the JaCoCo source."""

from datetime import datetime
import unittest
from unittest.mock import Mock, patch

from src.metric_collector import MetricCollector


class JaCoCoTest(unittest.TestCase):
    """Unit tests for the JaCoCo metrics."""

    def setUp(self):
        """Test fixture."""
        self.mock_response = Mock()
        self.sources = dict(source_id=dict(type="jacoco", parameters=dict(url="http://jacoco/")))

    def test_uncovered_lines(self):
        """Test that the number of uncovered lines is returned."""
        self.mock_response.text = "<report><counter type='LINE' missed='2' /></report>"
        metric = dict(type="uncovered_lines", sources=self.sources, addition="sum")
        with patch("requests.get", return_value=self.mock_response):
            response = MetricCollector(metric).get()
        self.assertEqual("2", response["sources"][0]["value"])

    def test_uncovered_branches(self):
        """Test that the number of uncovered branches is returned."""
        self.mock_response.text = "<report><counter type='BRANCH' missed='4' /></report>"
        metric = dict(type="uncovered_branches", sources=self.sources, addition="sum")
        with patch("requests.get", return_value=self.mock_response):
            response = MetricCollector(metric).get()
        self.assertEqual("4", response["sources"][0]["value"])

    def test_source_up_to_dateness(self):
        """Test that the source age in days is returned."""
        mock_response = Mock()
        mock_response.text = """<?xml version="1.0"?>
        <report>
            <sessioninfo dump="1553821197442"/>
        </report>"""
        metric = dict(type="source_up_to_dateness", sources=self.sources, addition="sum")
        with patch("requests.get", return_value=mock_response):
            response = MetricCollector(metric).get()
        expected_age = (datetime.utcnow() - datetime.utcfromtimestamp(1553821197.442)).days
        self.assertEqual(str(expected_age), response["sources"][0]["value"])
