"""Unit tests for the Cobertura source."""

import io
import zipfile
from datetime import datetime

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class CoberturaTest(SourceCollectorTestCase):
    """Unit tests for the Cobertura metrics."""

    def setUp(self):
        super().setUp()
        self.sources = dict(source_id=dict(type="cobertura", parameters=dict(url="https://cobertura/")))

    async def test_uncovered_lines(self):
        """Test that the number of uncovered lines and the total number of lines are returned."""
        metric = dict(type="uncovered_lines", sources=self.sources, addition="sum")
        response = await self.collect(metric, get_request_text="<coverage lines-covered='4' lines-valid='6' />")
        self.assert_measurement(response, value="2", total="6")

    async def test_uncovered_branches(self):
        """Test that the number of uncovered branches is returned."""
        metric = dict(type="uncovered_branches", sources=self.sources, addition="sum")
        response = await self.collect(
            metric, get_request_text="<coverage branches-covered='6' branches-valid='10' />")
        self.assert_measurement(response, value="4", total="10")

    async def test_source_up_to_dateness(self):
        """Test that the source age in days is returned."""
        metric = dict(type="source_up_to_dateness", sources=self.sources, addition="sum")
        response = await self.collect(metric, get_request_text='<coverage timestamp="1553821197442" />')
        expected_age = (datetime.utcnow() - datetime.utcfromtimestamp(1553821197.442)).days
        self.assert_measurement(response, value=str(expected_age))

    async def test_zipped_report(self):
        """Test that a zipped report can be read."""
        self.sources["source_id"]["parameters"]["url"] = "https://cobertura.zip"
        metric = dict(type="uncovered_lines", sources=self.sources, addition="sum")
        bytes_io = io.BytesIO()
        with zipfile.ZipFile(bytes_io, mode="w") as zipped_cobertura_report:
            zipped_cobertura_report.writestr("covertura.xml", "<coverage lines-covered='4' lines-valid='6' />")
        response = await self.collect(metric, get_request_content=bytes_io.getvalue())
        self.assert_measurement(response, value="2", total="6")
