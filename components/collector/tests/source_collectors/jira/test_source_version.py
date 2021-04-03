"""Unit tests for the Jira source version collector."""

from .base import JiraTestCase


class JiraSourceVersionTest(JiraTestCase):
    """Unit tests for the Jira source version collector."""

    METRIC_TYPE = "source_version"
    METRIC_ADDITION = "min"

    async def test_version(self):
        """Test that the Jira version is returned."""
        response = await self.collect(get_request_json_return_value=dict(version="8.3.1"))
        self.assert_measurement(response, value="8.3.1")
