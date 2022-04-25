"""Unit tests for the SARIF JSON security warnings collector."""

from re import I
from ..source_collector_test_case import SourceCollectorTestCase


class SARIFJSONSecurityWarningsTest(SourceCollectorTestCase):
    """Unit tests for the security warning metric."""

    SOURCE_TYPE = "sarif_json"
    METRIC_TYPE = "security_warnings"

    async def test_warnings(self):
        """Test the number of security warnings."""
        vulnerabilities_json = dict(
            runs=[
                dict(
                    tool=dict(
                        driver=dict(
                            rules=[
                                dict(
                                    id="CVE-2022-42",
                                    shortDescription=dict(text="CVE-2022-42"),
                                    fullDescription=dict(text="An issue was discovered ..."),
                                    helpUri="https://avd.aquasec.com/nvd/cve-2022-42",
                                )
                            ]
                        )
                    )
                )
            ]
        )
        expected_entities = [
            dict(
                key="CVE-2022-42",
                title="CVE-2022-42",
                description="An issue was discovered ...",
                url="https://avd.aquasec.com/nvd/cve-2022-42",
            )
        ]
        response = await self.collect(get_request_json_return_value=vulnerabilities_json)
        self.assert_measurement(response, value="1", entities=expected_entities)
