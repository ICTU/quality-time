"""Unit tests for the OpenVAS source."""

from datetime import datetime, timezone

from .source_collector_test_case import SourceCollectorTestCase


class OpenVASTest(SourceCollectorTestCase):
    """Unit tests for the OpenVAS metrics."""

    def setUp(self):
        super().setUp()
        self.sources = dict(source_id=dict(type="openvas", parameters=dict(url="https://openvas.xml")))

    def test_warnings(self):
        """Test that the number of warnings is returned."""
        openvas_xml = """<?xml version="1.0"?>
<report>
    <results>
        <result id="id">
            <name>Name</name>
            <description>Description</description>
            <threat>Low</threat>
            <host>1.2.3.4</host>
            <port>80/tcp</port>
        </result>
    </results>
</report>"""
        metric = dict(type="security_warnings", addition="sum", sources=self.sources)
        response = self.collect(metric, get_request_text=openvas_xml)
        self.assert_entities(
            [dict(key="id", severity="Low", name="Name", description="Description", host="1.2.3.4", port="80/tcp")],
            response)
        self.assert_value("1", response)

    def test_source_up_to_dateness(self):
        """Test that the report age in days is returned."""
        openvas_xml = """
<report extension="xml" type="scan" content_type="text/xml">
    <name>2019-04-09T17:56:14Z</name>
    <creation_time>2019-04-09T17:56:14Z</creation_time>
    <modification_time>2019-04-09T18:05:40Z</modification_time>
</report>"""
        metric = dict(type="source_up_to_dateness", addition="max", sources=self.sources)
        response = self.collect(metric, get_request_text=openvas_xml)
        expected_age = (datetime.now(timezone.utc) - datetime(2019, 4, 9, 17, 56, 14, tzinfo=timezone.utc)).days
        self.assert_value(str(expected_age), response)
