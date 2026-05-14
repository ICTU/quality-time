"""Unit tests for the Jenkins source version collector."""

from .base import JenkinsTestCase


class JenkinsSourceVersionTest(JenkinsTestCase):
    """Unit tests for the Jenkins source version collector."""

    METRIC_TYPE = "source_version"

    async def test_version(self):
        """Test that the Jenkins version is returned."""
        measurement = await self.collect_measurement(
            get_request_headers={"X-Jenkins": "2.9.2"}, get_request_json_return_value={}
        )
        self.assert_measurement(measurement, value="2.9.2")

    async def test_newer_version(self):
        """Test that the Jenkins version is returned, and a message that a newer version is available."""
        measurement = await self.collect_measurement(
            get_request_headers={"X-Jenkins": "2.9.2"}, get_request_json_return_value={"tag_name": "2.9.3"}
        )
        self.assert_measurement(measurement, value="2.9.2", info_message="Latest available version is 2.9.3")
