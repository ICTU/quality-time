"""Unit tests for the GitLab source version collector."""

from .base import GitLabTestCase


class GitLabSourceVersionTest(GitLabTestCase):
    """Unit tests for the GitLab source version collector."""

    METRIC_TYPE = "source_version"

    async def test_version(self):
        """Test that the GitLab version is returned."""
        measurement = await self.collect_measurement(get_request_json_return_value={"version": "13.7.4"})
        self.assert_measurement(measurement, value="13.7.4")

    async def test_ee_version(self):
        """Test that the GitLab Enterprise Edition version is returned."""
        measurement = await self.collect_measurement(get_request_json_return_value={"version": "14.5.4-ee"})
        self.assert_measurement(measurement, value="14.5.4")
