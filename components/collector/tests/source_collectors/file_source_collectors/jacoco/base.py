"""Base classes for the JaCoCo coverage report collectoes."""

import io
import zipfile

from ...source_collector_test_case import SourceCollectorTestCase


class JaCoCoTestCase(SourceCollectorTestCase):
    """Base class for JaCoCo collectors."""

    METRIC_TYPE = "Subclass responsibility"
    METRIC_ADDITION = "sum"
    JACOCO_XML = """
    <report>
        <sessioninfo dump="1553821197442"/>
        <counter type='LINE' missed='2' covered='4'/>
        <counter type='BRANCH' missed='2' covered='4'/>
    </report>
    """

    def setUp(self):
        """Extend to set up the sources and metric under test."""
        super().setUp()
        self.sources = dict(source_id=dict(type="jacoco", parameters=dict(url="https://jacoco/")))
        self.metric = dict(type=self.METRIC_TYPE, sources=self.sources, addition=self.METRIC_ADDITION)

    def zipped_report(self, filename: str = None, contents: str = None) -> bytes:
        """Return a zipped JaCoCo report."""
        bytes_io = io.BytesIO()
        with zipfile.ZipFile(bytes_io, mode="w") as zipped_jacoco_report:
            zipped_jacoco_report.writestr(filename or "jacoco.xml", contents or self.JACOCO_XML)
        return bytes_io.getvalue()


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
        response = await self.collect(self.metric, get_request_content=self.zipped_report())
        self.assert_measurement(response, value="2", total="6")
