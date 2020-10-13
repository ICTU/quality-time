"""Unit tests for the Generic Warning source."""

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class GenericSecurityWarningsTest(SourceCollectorTestCase):
    """Unit tests for the security warning metric."""

    async def test_warnings(self):
        """Test the number of security warnings."""
        sources = dict(source_id=dict(type="generic", parameters=dict(url="generic.json", severities=["high"])))
        metric = dict(type="security_warnings", sources=sources, addition="sum")
        vulnerabilities_json = dict(
            vulnerabilities=[
                {
                      'title': 'ISO27001:2013 A9',
                      'description': 'Application does not meet the Access Control Requirements since 2-fa is not enforced',
                      'severity': 'high',
                    } ])
        expected_entities = [
            dict(
                key='4c3462695bd4013b1dcfbb9da9aae1b9',
                title = 'ISO27001:2013 A9',
                description='Application does not meet the Access Control Requirements since 2-fa is not enforced',
                severity='high')]
        response = await self.collect(metric, get_request_json_return_value=vulnerabilities_json)
        self.assert_measurement(response, value="1", entities=expected_entities)
