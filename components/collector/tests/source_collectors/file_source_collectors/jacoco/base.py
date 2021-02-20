"""Base classes for the JaCoCo coverage report collectoes."""

from ...source_collector_test_case import SourceCollectorTestCase


class JaCoCoTestCase(SourceCollectorTestCase):  # skipcq: PTC-W0046
    """Base class for JaCoCo collectors."""

    SOURCE_TYPE = "jacoco"
    JACOCO_XML = "Subclass responsibility"


class JaCoCoCommonTestsMixin:
    """Tests common to all JaCoCo collectors."""

    async def test_zipped_report_without_xml(self):
        """Test that a zip file without xml files throws an exception."""
        self.sources["source_id"]["parameters"]["url"] = "https://jacoco.zip"
        report = self.zipped_report(
            "jacoco.html", "<html><body><p>Oops, user included the HTML instead of the XML</p></body></html>"
        )
        response = await self.collect(self.metric, get_request_content=report)
        self.assert_measurement(response, value=None, connection_error="Zipfile contains no files with extension xml")


class JaCoCoCommonCoverageTestsMixin:
    """Tests common to JaCoCo coverage collectors."""

    async def test_coverage(self):
        """Test that the number of uncovered lines/branches and the total number of lines/branches are returned."""
        response = await self.collect(self.metric, get_request_text=self.JACOCO_XML)
        self.assert_measurement(response, value="2", total="6")

    async def test_zipped_report(self):
        """Test that a zipped report can be read."""
        self.sources["source_id"]["parameters"]["url"] = "https://jacoco.zip"
        response = await self.collect(
            self.metric, get_request_content=self.zipped_report("jacoco.xml", self.JACOCO_XML)
        )
        self.assert_measurement(response, value="2", total="6")
