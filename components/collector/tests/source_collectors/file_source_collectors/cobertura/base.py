"""Base class for Cobertura unit tests."""

import io
import zipfile

from ...source_collector_test_case import SourceCollectorTestCase


class CoberturaTestCase(SourceCollectorTestCase):
    """Base class for testing Cobertura collectors."""

    COBERTURA_XML = "Subclass responsibility"
    METRIC_TYPE = "Subclass responsibility"
    METRIC_ADDITION = "sum"

    def setUp(self):
        """Extend to create source and metric fixtures."""
        super().setUp()
        self.sources = dict(source_id=dict(type="cobertura", parameters=dict(url="https://cobertura/")))
        self.metric = dict(type=self.METRIC_TYPE, sources=self.sources, addition=self.METRIC_ADDITION)

    def zipped_report(self) -> bytes:
        """Create a zipped Cobertura report."""
        bytes_io = io.BytesIO()
        with zipfile.ZipFile(bytes_io, mode="w") as zipped_cobertura_report:
            zipped_cobertura_report.writestr("cobertura.xml", self.COBERTURA_XML)
        return bytes_io.getvalue()


class CoberturaCoverageTestsMixin:
    """Tests for Cobertura coverage collectors."""

    async def test_uncovered_lines(self):
        """Test that the number of uncovered lines and the total number of lines are returned."""
        response = await self.collect(self.metric, get_request_text=self.COBERTURA_XML)
        self.assert_measurement(response, value="4", total="10")

    async def test_zipped_report(self):
        """Test that a zipped report can be read."""
        self.sources["source_id"]["parameters"]["url"] = "https://cobertura.zip"
        response = await self.collect(self.metric, get_request_content=self.zipped_report())
        self.assert_measurement(response, value="4", total="10")
