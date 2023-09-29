"""Unit tests for the Harbor JSON security warnings collector."""

from typing import ClassVar

from source_collectors.harbor_json.security_warnings import HarborJSON

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class HarborJSONSecurityWarningsTest(SourceCollectorTestCase):
    """Unit tests for the security warning metric."""

    SOURCE_TYPE = "harbor_json"
    METRIC_TYPE = "security_warnings"
    VULNERABILITIES_JSON: ClassVar[HarborJSON] = {
        "application/vnd.security.vulnerability.report; version=1.1": {
            "vulnerabilities": [
                {
                    "id": "CVE-2011-3374",
                    "package": "apt",
                    "version": "2.2.4",
                    "fix_version": "2.2.5",
                    "severity": "Low",
                    "description": "It was found that apt-key in apt, all versions, do not correctly validate ...",
                    "links": ["https://avd.aquasec.com/nvd/cve-2011-3374"],
                },
                {
                    "id": "CVE-2020-22218",
                    "package": "libssh2-1",
                    "version": "1.9.0-2",
                    "fix_version": "",
                    "severity": "High",
                    "description": "An issue was discovered in function _libssh2_packet_add in libssh2 1.10.0 ...",
                    "links": ["https://avd.aquasec.com/nvd/cve-2020-22218"],
                },
            ],
        },
    }
    EXPECTED_ENTITIES: ClassVar[list[dict[str, str]]] = [
        {
            "key": "CVE-2011-3374@apt@2_2_4",
            "vulnerability_id": "CVE-2011-3374",
            "package": "apt",
            "description": "It was found that apt-key in apt, all versions, do not correctly validate ...",
            "severity": "Low",
            "version": "2.2.4",
            "fix_version": "2.2.5",
            "url": "https://avd.aquasec.com/nvd/cve-2011-3374",
        },
        {
            "key": "CVE-2020-22218@libssh2-1@1_9_0-2",
            "vulnerability_id": "CVE-2020-22218",
            "package": "libssh2-1",
            "description": "An issue was discovered in function _libssh2_packet_add in libssh2 1.10.0 ...",
            "severity": "High",
            "version": "1.9.0-2",
            "fix_version": "",
            "url": "https://avd.aquasec.com/nvd/cve-2020-22218",
        },
    ]

    async def test_warnings(self):
        """Test the number of security warnings."""
        response = await self.collect(get_request_json_return_value=self.VULNERABILITIES_JSON)
        self.assert_measurement(response, value="2", entities=self.EXPECTED_ENTITIES)

    async def test_warning_severity(self):
        """Test the number of security warnings when specifying severities."""
        self.set_source_parameter("severities", ["high", "critical"])
        response = await self.collect(get_request_json_return_value=self.VULNERABILITIES_JSON)
        self.assert_measurement(response, value="1", entities=[self.EXPECTED_ENTITIES[1]])
