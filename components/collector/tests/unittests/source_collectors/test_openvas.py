"""Unit tests for the OpenVAS source."""

from datetime import datetime, timezone
import unittest
from unittest.mock import Mock, patch

from metric_collectors import MetricCollector


class OpenVASTest(unittest.TestCase):
    """Unit tests for the OpenVAS metrics."""

    def setUp(self):
        self.mock_response = Mock()
        self.sources = dict(source_id=dict(type="openvas", parameters=dict(url="http://openvas.xml")))
        self.datamodel = dict(
            sources=dict(openvas=dict(parameters=dict(severities=dict(values=["log", "low", "medium", "high"])))))

    def test_warnings(self):
        """Test that the number of warnings is returned."""
        self.mock_response.text = """<?xml version="1.0"?>
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
        with patch("requests.get", return_value=self.mock_response):
            response = MetricCollector(metric, self.datamodel).get()
        self.assertEqual(
            [dict(key="id", severity="Low", name="Name", description="Description", host="1.2.3.4", port="80/tcp")],
            response["sources"][0]["entities"])
        self.assertEqual("1", response["sources"][0]["value"])

    def test_source_up_to_dateness(self):
        """Test that the report age in days is returned."""
        self.mock_response.text = """
<report extension="xml" type="scan" content_type="text/xml">
    <name>2019-04-09T17:56:14Z</name>
    <creation_time>2019-04-09T17:56:14Z</creation_time>
    <modification_time>2019-04-09T18:05:40Z</modification_time>
</report>"""
        metric = dict(type="source_up_to_dateness", addition="max", sources=self.sources)
        with patch("requests.get", return_value=self.mock_response):
            response = MetricCollector(metric, self.datamodel).get()
        expected_age = (datetime.now(timezone.utc) - datetime(2019, 4, 9, 17, 56, 14, tzinfo=timezone.utc)).days
        self.assertEqual(str(expected_age), response["sources"][0]["value"])
