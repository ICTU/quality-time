"""Unit tests for the Axe-core source version collector."""

from .base import AxeCoreTestCase


class AxeCoreSourceVersionTest(AxeCoreTestCase):
    """Unit tests for the source version collector."""

    METRIC_TYPE = "source_version"
    METRIC_ADDITION = "min"
    AXE_VERSION = "4.1.3"

    async def test_source_version(self):
        """Test that the Axe-core version is returned."""
        axe_json = {"testEngine": {"version": self.AXE_VERSION}}
        response = await self.collect(get_request_json_return_value=axe_json)
        self.assert_measurement(response, value=self.AXE_VERSION)

    async def test_source_version_in_list(self):
        """Test that the Axe-core version is returned."""
        axe_json = [{"testEngine": {"version": self.AXE_VERSION}}]
        response = await self.collect(get_request_json_return_value=axe_json)
        self.assert_measurement(response, value=self.AXE_VERSION)
