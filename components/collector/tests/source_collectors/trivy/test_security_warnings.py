"""Unit tests for the Trivy JSON security warnings collector."""

from typing import ClassVar

from source_collectors.trivy.security_warnings import TrivyJSON

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class TrivyJSONSecurityWarningsTest(SourceCollectorTestCase):
    """Unit tests for the security warning metric."""

    SOURCE_TYPE = "trivy_json"
    METRIC_TYPE = "security_warnings"
    VULNERABILITIES_JSON: ClassVar[TrivyJSON] = [
        {
            "Target": "php-app/composer.lock",
            "Vulnerabilities": None,
        },
        {
            "Target": "trivy-ci-test (alpine 3.7.1)",
            "Vulnerabilities": [
                {
                    "VulnerabilityID": "CVE-2018-16840",
                    "PkgName": "curl",
                    "InstalledVersion": "7.61.0-r0",
                    "FixedVersion": "7.61.1-r1",
                    "Title": 'curl: Use-after-free when closing "easy" handle in Curl_close()',
                    "Description": "A heap use-after-free flaw was found in curl versions from 7.59.0 through ...",
                    "Severity": "HIGH",
                    "References": [
                        "https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-16840",
                    ],
                },
                {
                    "VulnerabilityID": "CVE-2019-3822",
                    "PkgName": "curl",
                    "InstalledVersion": "7.61.1-r0",
                    "FixedVersion": "7.61.2-r2",
                    "Title": "curl: NTLMv2 type-3 header stack buffer overflow",
                    "Description": "libcurl versions from 7.36.0 to before 7.64.0 are vulnerable to ...",
                    "Severity": "MEDIUM",
                    "References": [
                        "https://curl.haxx.se/docs/CVE-2019-3822.html",
                        "https://lists.apache.org/thread.html",
                    ],
                },
            ],
        },
    ]
    EXPECTED_ENTITIES: ClassVar[list[dict[str, str]]] = [
        {
            "key": "CVE-2018-16840@curl@trivy-ci-test (alpine 3_7_1)",
            "vulnerability_id": "CVE-2018-16840",
            "title": 'curl: Use-after-free when closing "easy" handle in Curl_close()',
            "description": "A heap use-after-free flaw was found in curl versions from 7.59.0 through ...",
            "level": "HIGH",
            "package_name": "curl",
            "installed_version": "7.61.0-r0",
            "fixed_version": "7.61.1-r1",
            "url": "https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-16840",
        },
        {
            "key": "CVE-2019-3822@curl@trivy-ci-test (alpine 3_7_1)",
            "vulnerability_id": "CVE-2019-3822",
            "title": "curl: NTLMv2 type-3 header stack buffer overflow",
            "description": "libcurl versions from 7.36.0 to before 7.64.0 are vulnerable to ...",
            "level": "MEDIUM",
            "package_name": "curl",
            "installed_version": "7.61.1-r0",
            "fixed_version": "7.61.2-r2",
            "url": "https://curl.haxx.se/docs/CVE-2019-3822.html",
        },
    ]

    async def test_warnings(self):
        """Test the number of security warnings."""
        response = await self.collect(get_request_json_return_value=self.VULNERABILITIES_JSON)
        self.assert_measurement(response, value="2", entities=self.EXPECTED_ENTITIES)

    async def test_warning_levels(self):
        """Test the number of security warnings when specifying a level."""
        self.set_source_parameter("levels", ["high", "critical"])
        response = await self.collect(get_request_json_return_value=self.VULNERABILITIES_JSON)
        self.assert_measurement(response, value="1", entities=[self.EXPECTED_ENTITIES[0]])
