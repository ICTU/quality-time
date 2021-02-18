"""Unit tests for the Generic JSON security warnings collector."""

from ...source_collector_test_case import SourceCollectorTestCase


class GenericJSONSecurityWarningsTest(SourceCollectorTestCase):
    """Unit tests for the security warning metric."""

    async def test_warnings(self):
        """Test the number of security warnings."""
        sources = dict(source_id=dict(type="generic_json", parameters=dict(url="generic.json", severities=["high"])))
        metric = dict(type="security_warnings", sources=sources, addition="sum")
        vulnerabilities_json = dict(
            vulnerabilities=[
                dict(
                    title="ISO27001:2013 A9",
                    description="Application does not meet the Access Control Requirements",
                    severity="high",
                )
            ]
        )
        expected_entities = [
            dict(
                key="4fff19e8a55b0dac211e16d105dbaccb",
                title="ISO27001:2013 A9",
                description="Application does not meet the Access Control Requirements",
                severity="high",
            )
        ]
        response = await self.collect(metric, get_request_json_return_value=vulnerabilities_json)
        self.assert_measurement(response, value="1", entities=expected_entities)
