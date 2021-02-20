"""Unit tests for the OWASP ZAP security warnings collector."""

from collector_utilities.functions import md5_hash

from .base import OWASPZAPTestCase


class OWASPZAPSecurityWarningsTest(OWASPZAPTestCase):
    """Unit tests for the OWASP ZAP security warnings collector."""

    METRIC_TYPE = "security_warnings"
    OWASP_ZAP_XML = """<?xml version="1.0"?>
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
    WARNING_NAME = "X-Content-Type-Options Header Missing"
    WARNING_DESCRIPTION = "The Anti-MIME-Sniffing header X-Content-Type-Options was not set to 'nosniff'."
    WARNING_RISK = "Low (Medium)"

    async def test_warnings(self):
        """Test that the number of security warnings is returned."""
        response = await self.collect(get_request_text=self.OWASP_ZAP_XML)
        url1 = "http://www.hackazon.com/products_pictures/Ray_Ban.jpg"
        url2 = "http://www.hackazon.com/products_pictures/How_to_Marry_a_Millionaire.jpg"
        expected_entities = [
            dict(
                key=md5_hash(f"X-Content-Type-Options Header Missing:10021:16:15:3:GET:{url1}"),
                old_key=md5_hash(f"10021:16:15:3:GET:{url1}"),
                name=self.WARNING_NAME,
                description=self.WARNING_DESCRIPTION,
                location=f"GET {url1}",
                uri=url1,
                risk=self.WARNING_RISK,
            ),
            dict(
                key=md5_hash(f"X-Content-Type-Options Header Missing:10021:16:15:3:GET:{url2}"),
                old_key=md5_hash(f"10021:16:15:3:GET:{url2}"),
                name=self.WARNING_NAME,
                description=self.WARNING_DESCRIPTION,
                location=f"GET {url2}",
                uri=url2,
                risk=self.WARNING_RISK,
            ),
        ]
        self.assert_measurement(response, value="2", entities=expected_entities)

    async def test_variable_url_regexp(self):
        """Test that parts of URLs can be ignored."""
        self.set_source_parameter("variable_url_regexp", ["[A-Za-z_]+.jpg"])
        response = await self.collect(get_request_text=self.OWASP_ZAP_XML)
        stable_url = "http://www.hackazon.com/products_pictures/variable-part-removed"
        expected_entities = [
            dict(
                key=md5_hash(f"X-Content-Type-Options Header Missing:10021:16:15:3:GET:{stable_url}"),
                old_key=md5_hash(f"10021:16:15:3:GET:{stable_url}"),
                name=self.WARNING_NAME,
                uri=stable_url,
                description=self.WARNING_DESCRIPTION,
                location=f"GET {stable_url}",
                risk=self.WARNING_RISK,
            )
        ]
        self.assert_measurement(response, value="1", entities=expected_entities)
