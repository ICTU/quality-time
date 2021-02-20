"""Unit tests for the Pyup.io Safety security warnings collector."""

from ...source_collector_test_case import SourceCollectorTestCase


class PyupioSafetyTest(SourceCollectorTestCase):
    """Unit tests for the security warning collector."""

    SOURCE_TYPE = "pyupio_safety"
    METRIC_TYPE = "security_warnings"

    async def test_warnings(self):
        """Test the number of security warnings."""
        pyupio_json = [["ansible", "<1.9.2", "1.8.5", "Ansible before 1.9.2 does not ...", "25625"]]
        response = await self.collect(self.metric, get_request_json_return_value=pyupio_json)
        expected_entities = [
            dict(
                package="ansible",
                key="25625",
                installed="1.8.5",
                affected="<1.9.2",
                vulnerability="Ansible before 1.9.2 does not ...",
            )
        ]
        self.assert_measurement(response, value="1", entities=expected_entities)
