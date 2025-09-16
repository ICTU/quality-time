"""Unit tests for the Trivy JSON security warnings collector."""

from .base import TrivyJSONTestCase


class TrivyJSONSecurityWarningsTest(TrivyJSONTestCase):
    """Unit tests for the security warning metric."""

    METRIC_TYPE = "security_warnings"

    def expected_entities(self):
        """Return the expected entities."""
        return [
            {
                "key": "CVE-2018-16840@curl@trivy-ci-test (alpine 3_7_1)",
                "vulnerability_id": "CVE-2018-16840",
                "title": 'curl: Use-after-free when closing "easy" handle in Curl_close()',
                "description": "A heap use-after-free flaw was found in curl versions from 7.59.0 through ...",
                "level": "HIGH",
                "package_name": "curl",
                "installed_version": "7.61.0-r0",
                "fixed_version": "7.61.1-r1",
                "uuid": "CVE-2018-16840",
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
                "fixed_version": "",
                "uuid": "CVE-2019-3822",
                "url": "https://curl.haxx.se/docs/CVE-2019-3822.html",
            },
            {
                "key": "CVE-2024-5432@python@trivy-ci-test (alpine 3_7_1)",
                "vulnerability_id": "CVE-2024-5432",
                "title": "Vulnerability without fixed version",
                "description": "This vulnerability has no fixed version field.",
                "level": "LOW",
                "package_name": "python",
                "installed_version": "3.13.1",
                "fixed_version": "",
                "uuid": "CVE-2024-5432",
                "url": "https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2024-5432",
            },
            {
                "key": "CVE-2025-6298@This vulnerability has no optional fields@trivy-ci-test (alpine 3_7_1)",
                "vulnerability_id": "CVE-2025-6298",
                "title": "CVE-2025-6298",
                "description": "",
                "package_name": "This vulnerability has no optional fields",
                "installed_version": "3.4.1",
                "level": "LOW",
                "fixed_version": "",
                "uuid": "CVE-2025-6298",
                "url": "",
            },
        ]

    async def test_warnings(self):
        """Test the number of security warnings."""
        for schema_version in self.SCHEMA_VERSIONS:
            with self.subTest(schema_version=schema_version):
                response = await self.collect(get_request_json_return_value=self.vulnerabilities_json(schema_version))
                self.assert_measurement(response, value="4", entities=self.expected_entities())

    async def test_warning_levels(self):
        """Test the number of security warnings when specifying a level."""
        self.set_source_parameter("levels", ["high", "critical"])
        for schema_version in self.SCHEMA_VERSIONS:
            with self.subTest(schema_version=schema_version):
                response = await self.collect(get_request_json_return_value=self.vulnerabilities_json(schema_version))
                self.assert_measurement(response, value="1", entities=[self.expected_entities()[0]])

    async def test_fix_available(self):
        """Test the number of security warnings when specifying fix availability."""
        self.set_source_parameter("fix_availability", ["fix available"])
        for schema_version in self.SCHEMA_VERSIONS:
            with self.subTest(schema_version=schema_version):
                response = await self.collect(get_request_json_return_value=self.vulnerabilities_json(schema_version))
                self.assert_measurement(response, value="1", entities=[self.expected_entities()[0]])

    async def test_fix_not_available(self):
        """Test the number of security warnings when specifying fix availability."""
        self.set_source_parameter("fix_availability", ["no fix available"])
        for schema_version in self.SCHEMA_VERSIONS:
            with self.subTest(schema_version=schema_version):
                response = await self.collect(get_request_json_return_value=self.vulnerabilities_json(schema_version))
                self.assert_measurement(response, value="3", entities=self.expected_entities()[1:])
