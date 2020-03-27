"""Unit tests for the Pyup.io Safety source."""

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class PyupioSafetyTest(SourceCollectorTestCase):
    """Unit tests for the security warning metric."""

    async def test_warnings(self):
        """Test the number of security warnings."""
        pyupio_json = [["ansible", "<1.9.2", "1.8.5", "Ansible before 1.9.2 does not ...", "25625"]]
        metric = dict(
            type="security_warnings", addition="sum",
            sources=dict(source_id=dict(type="pyupio_safety", parameters=dict(url="safety.json"))))
        response = await self.collect(metric, get_request_json_return_value=pyupio_json)
        expected_entities = [
            dict(package="ansible", key="25625", installed="1.8.5", affected="<1.9.2",
                 vulnerability="Ansible before 1.9.2 does not ...")]
        self.assert_measurement(response, value="1", entities=expected_entities)
