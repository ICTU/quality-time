"""Unit tests for the JaCoCo source."""

from datetime import datetime
from unittest.mock import Mock, patch

from .source_collector_test_case import SourceCollectorTestCase


class JaCoCoTest(SourceCollectorTestCase):
    """Unit tests for the JaCoCo metrics."""

    def setUp(self):
        super().setUp()
        self.mock_response = Mock()
        self.sources = dict(source_id=dict(type="jacoco", parameters=dict(url="http://jacoco/")))

    def test_uncovered_lines(self):
        """Test that the number of uncovered lines is returned."""
        self.mock_response.text = "<report><counter type='LINE' missed='2' /></report>"
        metric = dict(type="uncovered_lines", sources=self.sources, addition="sum")
        with patch("requests.get", return_value=self.mock_response):
            response = self.collect(metric)
        self.assert_value("2", response)

    def test_uncovered_branches(self):
        """Test that the number of uncovered branches is returned."""
        self.mock_response.text = "<report><counter type='BRANCH' missed='4' /></report>"
        metric = dict(type="uncovered_branches", sources=self.sources, addition="sum")
        with patch("requests.get", return_value=self.mock_response):
            response = self.collect(metric)
        self.assert_value("4", response)

    def test_source_up_to_dateness(self):
        """Test that the source age in days is returned."""
        self.mock_response.text = """<?xml version="1.0"?>
        <report>
            <sessioninfo dump="1553821197442"/>
        </report>"""
        metric = dict(type="source_up_to_dateness", sources=self.sources, addition="sum")
        with patch("requests.get", return_value=self.mock_response):
            response = self.collect(metric)
        expected_age = (datetime.utcnow() - datetime.utcfromtimestamp(1553821197.442)).days
        self.assert_value(str(expected_age), response)
