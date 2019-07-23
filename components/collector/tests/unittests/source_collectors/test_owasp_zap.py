"""Unit tests for the OWASP ZAP source."""

from datetime import datetime
import unittest
from unittest.mock import Mock, patch

from metric_collectors import MetricCollector


class OWASPZAPTest(unittest.TestCase):
    """Unit tests for the OWASP ZAP metrics."""

    def setUp(self):
        self.mock_response = Mock()
        self.sources = dict(sourceid=dict(type="owasp_zap", parameters=dict(url="http://owasp_zap.xml")))

    def test_warnings(self):
        """Test that the number of security warnings is returned."""
        self.mock_response.text = """<?xml version="1.0"?>
        <OWASPZAPReport version="2.7.0" generated="Thu, 28 Mar 2019 13:20:20">
            <site name="http://www.hackazon.com" host="www.hackazon.com" port="80" ssl="false">
                <alerts>
                    <alertitem>
                        <pluginid>10021</pluginid>
                        <alert>X-Content-Type-Options Header Missing</alert>
                        <name>X-Content-Type-Options Header Missing</name>
                        <riskcode>1</riskcode>
                        <confidence>2</confidence>
                        <riskdesc>Low (Medium)</riskdesc>
                        <desc>&lt;p&gt;The Anti-MIME-Sniffing header X-Content-Type-Options was not set to &apos;nosniff&apos;.</desc>
                        <instances>
                            <instance>
                                <uri>http://www.hackazon.com/products_pictures/Ray_Ban.jpg</uri>
                                <method>GET</method>
                                <param>X-Content-Type-Options</param>
                            </instance>
                            <instance>
                                <uri>http://www.hackazon.com/products_pictures/How_to_Marry_a_Millionaire.jpg</uri>
                                <method>GET</method>
                                <param>X-Content-Type-Options</param>
                            </instance>
                        </instances>
                        <count>759</count>
                        <solution>&lt;p&gt;Ensure that the application/web server sets the Content-Type header appropriately</solution>
                        <otherinfo>&lt;p&gt;This issue still applies to error type pages</otherinfo>
                        <reference>&lt;p&gt;http://msdn.microsoft.com/en-us/library/ie/gg622941%28v</reference>
                        <cweid>16</cweid>
                        <wascid>15</wascid>
                        <sourceid>3</sourceid>
                    </alertitem>
                </alerts>
            </site>
        </OWASPZAPReport>"""
        metric = dict(type="security_warnings", addition="sum", sources=self.sources)
        with patch("requests.get", return_value=self.mock_response):
            response = MetricCollector(metric).get()
        self.assertEqual(
            [
                dict(key="10021:16:15:3:GET:http://www.hackazon.com/products_pictures/Ray_Ban.jpg",
                     name="X-Content-Type-Options Header Missing",
                     description="The Anti-MIME-Sniffing header X-Content-Type-Options was not set to 'nosniff'.",
                     location="GET http://www.hackazon.com/products_pictures/Ray_Ban.jpg",
                     uri="http://www.hackazon.com/products_pictures/Ray_Ban.jpg", risk="Low (Medium)"),
                dict(key="10021:16:15:3:GET:http://www.hackazon.com/products_pictures/How_to_Marry_a_Millionaire.jpg",
                     name="X-Content-Type-Options Header Missing",
                     description="The Anti-MIME-Sniffing header X-Content-Type-Options was not set to 'nosniff'.",
                     location="GET http://www.hackazon.com/products_pictures/How_to_Marry_a_Millionaire.jpg",
                     uri="http://www.hackazon.com/products_pictures/How_to_Marry_a_Millionaire.jpg",
                     risk="Low (Medium)")],
            response["sources"][0]["entities"])
        self.assertEqual("2", response["sources"][0]["value"])

    def test_source_up_to_dateness(self):
        """Test that the source age in days is returned."""
        self.mock_response.text = """<?xml version="1.0"?>
        <OWASPZAPReport version="2.7.0" generated="Thu, 28 Mar 2019 13:20:20">
        </OWASPZAPReport>"""
        metric = dict(type="source_up_to_dateness", addition="max", sources=self.sources)
        with patch("requests.get", return_value=self.mock_response):
            response = MetricCollector(metric).get()
        expected_age = (datetime.now() - datetime(2019, 3, 28, 13, 20, 20)).days
        self.assertEqual(str(expected_age), response["sources"][0]["value"])
