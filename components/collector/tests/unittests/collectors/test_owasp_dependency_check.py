"""Unit tests for the OWASP Dependency Check source."""

from datetime import datetime, timedelta, timezone
import unittest
from unittest.mock import Mock, patch

from src.collector import collect_measurement


class OWASPDependencyCheckTest(unittest.TestCase):
    """Unit tests for the OWASP Dependency Check metrics."""

    def setUp(self):
        self.mock_response = Mock()
        self.sources = dict(
            sourceid=dict(type="owasp_dependency_check", parameters=dict(url="http://owasp_dependency_check.xml")))

    def test_warnings(self):
        """Test that the number of warnings is returned."""
        self.mock_response.text = """<?xml version="1.0"?>
        <analysis xmlns="https://jeremylong.github.io/DependencyCheck/dependency-check.1.8.xsd">
            <dependency isVirtual="false">
                <md5>12345</md5>
                <fileName>jquery.min.js</fileName>
                <filePath>/home/jenkins/workspace/hackazon-owaspdep/hackazon/js/jquery.min.js</filePath>
                <vulnerabilities>
                    <vulnerability source="NVD">
                        <name>CVE-2012-6708</name>
                        <severity>Medium</severity>
                        <cwe>CWE-79 Improper Neutralization of Input During Web Page Generation (XSS).</cwe>
                        <description>jQuery before 1.9.0 is vulnerable to Cross-site Scripting (XSS) attacks.</description>
                    </vulnerability>
                </vulnerabilities>
            </dependency>
        </analysis>"""
        metric = dict(type="security_warnings", addition="sum", sources=self.sources)
        with patch("requests.get", return_value=self.mock_response):
            response = collect_measurement(metric)
        self.assertEqual(
            [dict(key="/home/jenkins/workspace/hackazon-owaspdep/hackazon/js/jquery.min.js:CVE-2012-6708",
                  name="CVE-2012-6708", severity="Medium",
                  description="jQuery before 1.9.0 is vulnerable to Cross-site Scripting (XSS) attacks.",
                  location="/home/jenkins/workspace/hackazon-owaspdep/hackazon/js/jquery.min.js")],
            response["sources"][0]["units"])
        self.assertEqual("1", response["sources"][0]["value"])

    def test_source_up_to_dateness(self):
        """Test that the source age in days is returned."""
        self.mock_response.text = """<?xml version="1.0"?>
        <analysis xmlns="https://jeremylong.github.io/DependencyCheck/dependency-check.1.8.xsd">
            <projectInfo>
                <reportDate>2018-10-03T13:01:24.784+0200</reportDate>
            </projectInfo>
        </analysis>"""
        metric = dict(type="source_up_to_dateness", addition="max", sources=self.sources)
        with patch("requests.get", return_value=self.mock_response):
            response = collect_measurement(metric)
        tzinfo = timezone(timedelta(hours=2))
        expected_age = (datetime.now(tzinfo) - datetime(2018, 10, 3, 13, 1, 24, 784, tzinfo=tzinfo)).days
        self.assertEqual(str(expected_age), response["sources"][0]["value"])
