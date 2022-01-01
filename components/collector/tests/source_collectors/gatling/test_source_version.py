"""Unit tests for the Gatling source version collector."""

from .base import GatlingTestCase


class GatlingSourceVersionTest(GatlingTestCase):
    """Unit tests for the Gatling source version collector."""

    METRIC_TYPE = "source_version"

    async def test_source_version_empty_file(self):
        """Test that a default source version is returned."""
        response = await self.collect(get_request_text="")
        self.assert_measurement(response, value="0")

    async def test_source_version(self):
        """Test that the source version is returned."""
        response = await self.collect(get_request_text=self.GATLING_LOG)
        self.assert_measurement(response, value="3.3.1")
