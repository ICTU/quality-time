"""Unit tests for the OWASP ZAP source."""

import unittest
from unittest.mock import Mock, patch

from src.collector import collect_measurement


class OWASPZAPTest(unittest.TestCase):
    """Unit tests for the OWASP ZAP metrics."""

    def test_violations(self):
        """Test that the number of security warnings is returned."""
        mock_response = Mock()
        mock_response.text = """<?xml version="1.0"?>
        <OWASPZAPReport version="2.7.0" generated="Thu, 28 Mar 2019 13:20:20">
            <site name="http://www.hackazon.gros.ictu" host="www.hackazon.gros.ictu" port="80" ssl="false">
                <alerts>
                    <alertitem>
                        <pluginid>10021</pluginid>
                        <alert>X-Content-Type-Options Header Missing</alert>
                        <name>X-Content-Type-Options Header Missing</name>
                        <riskcode>1</riskcode>
                        <confidence>2</confidence>
                        <riskdesc>Low (Medium)</riskdesc>
                        <desc>&lt;p&gt;The Anti-MIME-Sniffing header X-Content-Type-Options was not set to &apos;nosniff&apos;. This allows older versions of Internet Explorer and Chrome to perform MIME-sniffing on the response body, potentially causing the response body to be interpreted and displayed as a content type other than the declared content type. Current (early 2014) and legacy versions of Firefox will use the declared content type (if one is set), rather than performing MIME-sniffing.&lt;/p&gt;</desc>
                        <instances>
                            <instance>
                                <uri>http://www.hackazon.gros.ictu/products_pictures/Ray_Ban_Aviator_Non_Polarized_Sunglasses_big_78ef2b.jpg</uri>
                                <method>GET</method>
                                <param>X-Content-Type-Options</param>
                            </instance>
                            <instance>
                                <uri>http://www.hackazon.gros.ictu/products_pictures/How_to_Marry_a_Millionaire_big_df6c63.jpg</uri>
                                <method>GET</method>
                                <param>X-Content-Type-Options</param>
                            </instance>
                        </instances>
                        <count>759</count>
                        <solution>&lt;p&gt;Ensure that the application/web server sets the Content-Type header appropriately, and that it sets the X-Content-Type-Options header to &apos;nosniff&apos; for all web pages.&lt;/p&gt;&lt;p&gt;If possible, ensure that the end user uses a standards-compliant and modern web browser that does not perform MIME-sniffing at all, or that can be directed by the web application/web server to not perform MIME-sniffing.&lt;/p&gt;</solution>
                        <otherinfo>&lt;p&gt;This issue still applies to error type pages (401, 403, 500, etc) as those pages are often still affected by injection issues, in which case there is still concern for browsers sniffing pages away from their actual content type.&lt;/p&gt;&lt;p&gt;At &quot;High&quot; threshold this scanner will not alert on client or server error responses.&lt;/p&gt;</otherinfo>
                        <reference>&lt;p&gt;http://msdn.microsoft.com/en-us/library/ie/gg622941%28v=vs.85%29.aspx&lt;/p&gt;&lt;p&gt;https://www.owasp.org/index.php/List_of_useful_HTTP_headers&lt;/p&gt;</reference>
                        <cweid>16</cweid>
                        <wascid>15</wascid>
                        <sourceid>3</sourceid>
                    </alertitem>
                </alerts>
            </site>
        </OWASPZAPReport>"""
        metric = dict(
            type="security_warnings",
            sources=dict(sourceid=dict(type="owasp_zap",
                                       parameters=dict(url="http://owasp_zap.xml"))))
        with patch("requests.get", return_value=mock_response):
            response = collect_measurement(metric)
        self.assertEqual([], response["sources"][0]["units"])
        self.assertEqual("1", response["sources"][0]["value"])
