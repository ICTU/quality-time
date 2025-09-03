"""Unit tests for the Anchore Jenkins plugin security warnings collector."""

from shared.utils.functions import md5_hash

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class AnchoreJenkinsPluginSecurityWarningsTest(SourceCollectorTestCase):
    """Unit tests for the Anchore Jenkins plugin security warnings collector."""

    METRIC_TYPE = "security_warnings"
    SOURCE_TYPE = "anchore_jenkins_plugin"

    def setUp(self) -> None:
        """Create the Anchore Jenkins plugin JSON fixture."""
        super().setUp()
        self.job_json = {"name": "job", "lastSuccessfulBuild": {"number": 42}}
        self.vulnerabilities_json = {
            "data": [
                ["tag", "CVE-000", "Low", "package", "None", "https://cve-000"],
                ["tag", "CVE-001", "Unknown", "package2", "v1.2.3", "https://cve-001"],
            ],
        }

    def create_entity(self, cve: str, package: str, severity: str = "Low", fix: str = "None") -> dict[str, str]:
        """Create an expected entity."""
        return {
            "key": md5_hash(f"tag:{cve}:{package}"),
            "tag": "tag",
            "cve": cve,
            "url": f"https://{cve.lower()}",
            "fix": fix,
            "severity": severity,
            "package": package,
            "uuid": cve,
        }

    async def test_warnings(self):
        """Test the number of security warnings."""
        response = await self.collect(get_request_json_side_effect=[self.job_json, self.vulnerabilities_json])
        expected_entities = [
            self.create_entity("CVE-000", "package"),
            self.create_entity("CVE-001", "package2", severity="Unknown", fix="v1.2.3"),
        ]
        self.assert_measurement(response, value="2", entities=expected_entities)

    async def test_filter_warnings_by_severity(self):
        """Test that the security warnings can be filtered by severity."""
        self.set_source_parameter("severities", ["Low"])
        response = await self.collect(get_request_json_side_effect=[self.job_json, self.vulnerabilities_json])
        expected_entities = [self.create_entity("CVE-000", "package")]
        self.assert_measurement(response, value="1", entities=expected_entities)

    async def test_filter_warnings_by_fix_availability(self):
        """Test that the security warnings can be filtered by fix availability."""
        self.set_source_parameter("fix_availability", ["no fix available"])
        response = await self.collect(get_request_json_side_effect=[self.job_json, self.vulnerabilities_json])
        expected_entities = [self.create_entity("CVE-000", "package")]
        self.assert_measurement(response, value="1", entities=expected_entities)
