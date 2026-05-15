"""Unit tests for the Jira source version collector."""

from .base import JiraTestCase


class JiraSourceVersionTest(JiraTestCase):
    """Unit tests for the Jira source version collector."""

    METRIC_TYPE = "source_version"

    async def test_version(self):
        """Test that the Jira version is returned."""
        measurement = await self.collect_measurement(get_request_json_return_value={"version": "8.3.1"})
        self.assert_measurement(measurement, value="8.3.1")
