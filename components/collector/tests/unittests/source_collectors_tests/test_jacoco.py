"""Unit tests for the JaCoCo source."""

import io
import zipfile
from datetime import datetime

from .source_collector_test_case import SourceCollectorTestCase


class JaCoCoTest(SourceCollectorTestCase):
    """Unit tests for the JaCoCo metrics."""

    def setUp(self):
        super().setUp()
        self.sources = dict(source_id=dict(type="jacoco", parameters=dict(url="https://jacoco/")))

    def test_uncovered_lines(self):
        """Test that the number of uncovered lines and the total number of lines are returned."""
        metric = dict(type="uncovered_lines", sources=self.sources, addition="sum")
        response = self.collect(
            metric, get_request_text="<report><counter type='LINE' missed='2' covered='4'/></report>")
        self.assert_measurement(response, value="2", total="6")

    def test_uncovered_branches(self):
        """Test that the number of uncovered branches is returned."""
        metric = dict(type="uncovered_branches", sources=self.sources, addition="sum")
        response = self.collect(
            metric, get_request_text="<report><counter type='BRANCH' missed='4' covered='6'/></report>")
        self.assert_measurement(response, value="4", total="10")

    def test_source_up_to_dateness(self):
        """Test that the source age in days is returned."""
        metric = dict(type="source_up_to_dateness", sources=self.sources, addition="sum")
        response = self.collect(metric, get_request_text='<report><sessioninfo dump="1553821197442"/></report>')
        expected_age = (datetime.utcnow() - datetime.utcfromtimestamp(1553821197.442)).days
        self.assert_measurement(response, value=str(expected_age))

    def test_zipped_report(self):
        """Test that a zipped report can be read."""
        self.sources["source_id"]["parameters"]["url"] = "https://jacoco.zip"
        metric = dict(type="uncovered_lines", sources=self.sources, addition="sum")
        with zipfile.ZipFile(bytes_io := io.BytesIO(), mode="w") as zipped_jacoco_report:
            zipped_jacoco_report.writestr(
                "jacoco.xml", "<report><counter type='LINE' missed='2' covered='4'/></report>")
        response = self.collect(metric, get_request_content=bytes_io.getvalue())
        self.assert_measurement(response, value="2", total="6")
