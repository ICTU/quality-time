"""Unit tests for the OWASP Dependency Check source."""

import unittest
from unittest.mock import Mock, patch

from src.collector import collect_measurement


class OWASPDependencyCheckTest(unittest.TestCase):
    """Unit tests for the OWASP Dependency Check metrics."""

    def test_violations(self):
        """Test that the number of violations is returned."""
        mock_response = Mock()
        mock_response.text = """<?xml version="1.0"?>
        <analysis xmlns="https://jeremylong.github.io/DependencyCheck/dependency-check.1.8.xsd">
            <dependency isVirtual="false">
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
        metric = dict(
            type="security_warnings",
            sources=dict(sourceid=dict(type="owasp_dependency_check",
                                       parameters=dict(url="http://owasp_dependency_check.xml"))))
        with patch("requests.get", return_value=mock_response):
            response = collect_measurement(metric)
        self.assertEqual([], response["sources"][0]["units"])
        self.assertEqual("1", response["sources"][0]["value"])
