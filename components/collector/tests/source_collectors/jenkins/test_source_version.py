"""Unit tests for the Jenkins source version collector."""

from .base import JenkinsTestCase


class JenkinsSourceVersionTest(JenkinsTestCase):
    """Unit tests for the Jenkins source version collector."""

    METRIC_TYPE = "source_version"

    async def test_version(self):
        """Test that the Jenkins version is returned."""
        response = await self.collect(get_request_headers={"X-Jenkins": "2.9.2"})
        self.assert_measurement(response, value="2.9.2")
