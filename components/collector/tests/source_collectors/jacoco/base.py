"""Base classes for the JaCoCo coverage report collectors."""

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class JaCoCoTestCase(SourceCollectorTestCase):
    """Base class for JaCoCo collectors."""

    SOURCE_TYPE = "jacoco"


class JaCoCoCommonTestsMixin:
    """Tests common to all JaCoCo collectors."""

    async def test_zipped_report_without_xml(self):
        """Test that a zip file without xml files throws an exception."""
        self.set_source_parameter("url", "https://example.org/jacoco.zip")
        report = self.zipped_report(
            ("jacoco.html", "<html><body><p>Oops, user included the HTML instead of the XML</p></body></html>"),
        )
        response = await self.collect(get_request_content=report)
        self.assert_measurement(response, connection_error="Zipfile contains no files with extension xml")


class JaCoCoCommonCoverageTestsMixin:
    """Tests common to JaCoCo coverage collectors."""

    JACOCO_XML = """
<report>
    <package>
        <class>
            <method>
                <counter type='LINE' missed='2' covered='4'/>
                <counter type='BRANCH' missed='2' covered='4'/>
            </method>
        </class>
        <class>
                    <method>
                        <counter type='LINE' missed='0' covered='3'/>
                        <counter type='BRANCH' missed='0' covered='3'/>
                    </method>
                </class>
    </package>
    <counter type='LINE' missed='2' covered='7'/>
    <counter type='BRANCH' missed='2' covered='7'/>
</report>
"""

    async def test_coverage(self):
        """Test that the number of uncovered lines/branches and the total number of lines/branches are returned."""
        response = await self.collect(get_request_text=self.JACOCO_XML)
        self.assert_measurement(response, value="2", total="9")

    async def test_zipped_report(self):
        """Test that a zipped report can be read."""
        self.set_source_parameter("url", "https://example.org/jacoco.zip")
        response = await self.collect(get_request_content=self.zipped_report(("jacoco.xml", self.JACOCO_XML)))
        self.assert_measurement(response, value="2", total="9")
