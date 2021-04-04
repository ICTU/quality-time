"""Unit tests for the Anchore Jenkins plugin security warnings collector."""

from collector_utilities.functions import md5_hash

from ..source_collector_test_case import SourceCollectorTestCase


class AnchoreJenkinsPluginSecurityWarningsTest(SourceCollectorTestCase):
    """Unit tests for the Anchore Jenkins plugin security warnings collector."""

    METRIC_TYPE = "security_warnings"
    SOURCE_TYPE = "anchore_jenkins_plugin"

    async def test_warnings(self):
        """Test the number of security warnings."""
        self.set_source_parameter("severities", ["Low"])
        vulnerabilities_json = dict(
            data=[
                ["tag", "CVE-000", "Low", "package", "None", "https://cve-000"],
                ["tag", "CVE-001", "Unknown", "package2", "None", "https://cve-001"],
            ]
        )
        response = await self.collect(
            get_request_json_side_effect=[dict(name="job", lastSuccessfulBuild=dict(number=42)), vulnerabilities_json]
        )
        expected_entities = [
            dict(
                key=md5_hash("tag:CVE-000:package"),
                tag="tag",
                cve="CVE-000",
                url="https://cve-000",
                fix="None",
                severity="Low",
                package="package",
            )
        ]
        self.assert_measurement(response, value="1", entities=expected_entities)
