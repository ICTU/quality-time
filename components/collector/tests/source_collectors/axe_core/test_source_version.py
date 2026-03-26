"""Unit tests for the Axe-core source version collector."""

from .base import AxeCoreTestCase


class AxeCoreSourceVersionTest(AxeCoreTestCase):
    """Unit tests for the source version collector."""

    METRIC_TYPE = "source_version"
    AXE_VERSION = "4.1.3"

    async def test_source_version(self):
        """Test that the Axe-core version is returned."""
        axe_json = {"testEngine": {"version": self.AXE_VERSION}}
        response = await self.collect(get_request_json_side_effect=[{}, axe_json])
        self.assert_measurement(response, value=self.AXE_VERSION)

    async def test_source_version_in_list(self):
        """Test that the Axe-core version is returned."""
        axe_json = [{"testEngine": {"version": self.AXE_VERSION}}]
        response = await self.collect(get_request_json_side_effect=[{}, axe_json])
        self.assert_measurement(response, value=self.AXE_VERSION)

    async def test_newer_version_available(self):
        """Test that an information message with the new version is returned."""
        axe_json = {"testEngine": {"version": self.AXE_VERSION}}
        response = await self.collect(get_request_json_side_effect=[{"tag_name": "v4.1.4"}, axe_json])
        self.assert_measurement(response, value=self.AXE_VERSION, info_message="Latest available version is 4.1.4")

    async def test_no_newer_version_available(self):
        """Test that no information message is returned if the latest version is the current version."""
        axe_json = {"testEngine": {"version": self.AXE_VERSION}}
        response = await self.collect(get_request_json_side_effect=[{"tag_name": self.AXE_VERSION}, axe_json])
        self.assert_measurement(response, value=self.AXE_VERSION)
