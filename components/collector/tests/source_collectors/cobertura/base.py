"""Base class for Cobertura unit tests."""

from typing import TYPE_CHECKING

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class CoberturaTestCase(SourceCollectorTestCase):
    """Base class for testing Cobertura collectors."""

    SOURCE_TYPE = "cobertura"


class CoberturaCoverageTestsMixin(CoberturaTestCase if TYPE_CHECKING else object):  # type: ignore[misc]
    """Tests for Cobertura coverage collectors."""

    COBERTURA_XML = "Subclass responsibility"

    async def test_uncovered_lines(self):
        """Test that the number of uncovered lines and the total number of lines are returned."""
        measurement = await self.collect_measurement(get_request_text=self.COBERTURA_XML)
        self.assert_measurement(measurement, value="4", total="10")

    async def test_zipped_report(self):
        """Test that a zipped report can be read."""
        self.set_source_parameter("url", "https://example.org/cobertura.zip")
        measurement = await self.collect_measurement(
            get_request_content=self.zipped_report(("cobertura.xml", self.COBERTURA_XML))
        )
        self.assert_measurement(measurement, value="4", total="10")
