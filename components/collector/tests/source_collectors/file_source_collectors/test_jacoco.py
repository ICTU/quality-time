"""Unit tests for the JaCoCo source."""

import io
import zipfile
from datetime import datetime

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class JaCoCoTest(SourceCollectorTestCase):
    """Unit tests for the JaCoCo metrics."""

    def setUp(self):
        super().setUp()
        self.sources = dict(source_id=dict(type="jacoco", parameters=dict(url="https://jacoco/")))

    async def test_uncovered_lines(self):
        """Test that the number of uncovered lines and the total number of lines are returned."""
        metric = dict(type="uncovered_lines", sources=self.sources, addition="sum")
        response = await self.collect(
            metric, get_request_text="<report><counter type='LINE' missed='2' covered='4'/></report>")
        self.assert_measurement(response, value="2", total="6")

    async def test_uncovered_branches(self):
        """Test that the number of uncovered branches is returned."""
        metric = dict(type="uncovered_branches", sources=self.sources, addition="sum")
        response = await self.collect(
            metric, get_request_text="<report><counter type='BRANCH' missed='4' covered='6'/></report>")
        self.assert_measurement(response, value="4", total="10")

    async def test_source_up_to_dateness(self):
        """Test that the source age in days is returned."""
        metric = dict(type="source_up_to_dateness", sources=self.sources, addition="sum")
        response = await self.collect(metric, get_request_text='<report><sessioninfo dump="1553821197442"/></report>')
        expected_age = (datetime.utcnow() - datetime.utcfromtimestamp(1553821197.442)).days
        self.assert_measurement(response, value=str(expected_age))

    async def test_zipped_report(self):
        """Test that a zipped report can be read."""
        self.sources["source_id"]["parameters"]["url"] = "https://jacoco.zip"
        metric = dict(type="uncovered_lines", sources=self.sources, addition="sum")
        bytes_io = io.BytesIO()
        with zipfile.ZipFile(bytes_io, mode="w") as zipped_jacoco_report:
            zipped_jacoco_report.writestr(
                "jacoco.xml", "<report><counter type='LINE' missed='2' covered='4'/></report>")
        response = await self.collect(metric, get_request_content=bytes_io.getvalue())
        self.assert_measurement(response, value="2", total="6")

    async def test_zipped_report_without_xml(self):
        """Test that a zip file without xml files throws an exception."""
        self.sources["source_id"]["parameters"]["url"] = "https://jacoco.zip"
        metric = dict(type="uncovered_lines", sources=self.sources, addition="sum")
        bytes_io = io.BytesIO()
        with zipfile.ZipFile(bytes_io, mode="w") as zipped_jacoco_report:
            zipped_jacoco_report.writestr(
                "jacoco.html", "<html><body><p>Oops, user included the HTML instead of the XML</p></body></html>")
        response = await self.collect(metric, get_request_content=bytes_io.getvalue())
        self.assert_measurement(response, value=None, connection_error="Zipfile contains no files with extension xml")