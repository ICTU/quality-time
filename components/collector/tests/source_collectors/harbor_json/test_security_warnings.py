"""Unit tests for the Harbor JSON security warnings collector."""

from typing import ClassVar

from .base import HarborJSONCollectorTestCase


class HarborJSONSecurityWarningsTest(HarborJSONCollectorTestCase):
    """Unit tests for the security warning metric."""

    METRIC_TYPE = "security_warnings"
    EXPECTED_ENTITIES: ClassVar[list[dict[str, str]]] = [
        {
            "key": "CVE-2011-3374@apt@2_2_4",
            "vulnerability_id": "CVE-2011-3374",
            "package": "apt",
            "description": "It was found that apt-key in apt, all versions, do not correctly validate ...",
            "severity": "Low",
            "version": "2.2.4",
            "fix_version": "2.2.5",
            "uuid": "CVE-2011-3374",
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
            "uuid": "CVE-2020-22218",
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

    async def test_warning_fix_available(self):
        """Test the number of security warnings when filtering by fix availability."""
        self.set_source_parameter("fix_availability", ["fix available"])
        response = await self.collect(get_request_json_return_value=self.VULNERABILITIES_JSON)
        self.assert_measurement(response, value="1", entities=[self.EXPECTED_ENTITIES[0]])

    async def test_warning_fix_not_available(self):
        """Test the number of security warnings when filtering by fix availability."""
        self.set_source_parameter("fix_availability", ["no fix available"])
        response = await self.collect(get_request_json_return_value=self.VULNERABILITIES_JSON)
        self.assert_measurement(response, value="1", entities=[self.EXPECTED_ENTITIES[1]])
