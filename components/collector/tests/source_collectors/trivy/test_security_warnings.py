"""Unit tests for the Trivy JSON security warnings collector."""

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class TrivyJSONSecurityWarningsTest(SourceCollectorTestCase):
    """Unit tests for the security warning metric."""

    SOURCE_TYPE = "trivy_json"
    METRIC_TYPE = "security_warnings"
    SCHEMA_VERSIONS = (1, 2)

    def vulnerabilities_json(self, schema_version: int = 1):
        """Return the Trivy Vulnerabilities JSON."""
        results = [
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
                        "FixedVersion": "",
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
        if schema_version == 1:
            return results
        return {"SchemaVersion": 2, "Results": results}

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
                "url": "https://curl.haxx.se/docs/CVE-2019-3822.html",
            },
        ]

    async def test_warnings(self):
        """Test the number of security warnings."""
        for schema_version in self.SCHEMA_VERSIONS:
            with self.subTest(schema_version=schema_version):
                response = await self.collect(get_request_json_return_value=self.vulnerabilities_json(schema_version))
                self.assert_measurement(response, value="2", entities=self.expected_entities())

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
                self.assert_measurement(response, value="1", entities=[self.expected_entities()[1]])
