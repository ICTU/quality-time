"""Base class for Trivy JSON collector unit tests."""

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class TrivyJSONTestCase(SourceCollectorTestCase):
    """Base class for Trivy JSON Unit tests."""

    SOURCE_TYPE = "trivy_json"
    SCHEMA_VERSIONS = (1, 2)

    def vulnerabilities_json(self, schema_version: int = 2):
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
                    {
                        "VulnerabilityID": "CVE-2024-5432",
                        "PkgName": "python",
                        "InstalledVersion": "3.13.1",
                        "Title": "Vulnerability without fixed version",
                        "Description": "This vulnerability has no fixed version field.",
                        "Severity": "LOW",
                        "References": ["https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2024-5432"],
                    },
                ],
            },
        ]
        if schema_version == 1:
            return results
        return {"SchemaVersion": 2, "CreatedAt": "2024-12-26T21:58:15.943876+05:30", "Results": results}
