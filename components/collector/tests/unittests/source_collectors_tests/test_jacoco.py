"""Unit tests for the JaCoCo source."""

from datetime import datetime

from .source_collector_test_case import SourceCollectorTestCase


class JaCoCoTest(SourceCollectorTestCase):
    """Unit tests for the JaCoCo metrics."""

    def setUp(self):
        super().setUp()
        self.sources = dict(source_id=dict(type="jacoco", parameters=dict(url="http://jacoco/")))

    def test_uncovered_lines(self):
        """Test that the number of uncovered lines is returned."""
        metric = dict(type="uncovered_lines", sources=self.sources, addition="sum")
        response = self.collect(metric, get_request_text="<report><counter type='LINE' missed='2' /></report>")
        self.assert_value("2", response)

    def test_uncovered_branches(self):
        """Test that the number of uncovered branches is returned."""
        metric = dict(type="uncovered_branches", sources=self.sources, addition="sum")
        response = self.collect(metric, get_request_text="<report><counter type='BRANCH' missed='4' /></report>")
        self.assert_value("4", response)

    def test_source_up_to_dateness(self):
        """Test that the source age in days is returned."""
        metric = dict(type="source_up_to_dateness", sources=self.sources, addition="sum")
        response = self.collect(metric, get_request_text='<report><sessioninfo dump="1553821197442"/></report>')
        expected_age = (datetime.utcnow() - datetime.utcfromtimestamp(1553821197.442)).days
        self.assert_value(str(expected_age), response)
