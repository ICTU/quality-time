"""Unit tests for the Robot Framework source version collector."""

from .base import RobotFrameworkTestCase


class RobotFrameworkSourceVersionTest(RobotFrameworkTestCase):
    """Unit test for the Robot Framework source version collector."""

    METRIC_TYPE = "source_version"

    async def test_source_version4(self):
        """Test that the Robot Framework version is returned."""
        response = await self.collect(get_request_text=self.ROBOT_FRAMEWORK_XML_V4, get_request_json_return_value={})
        self.assert_measurement(response, value="4.0b3.dev1")

    async def test_source_version5(self):
        """Test that the Robot Framework version is returned."""
        response = await self.collect(get_request_text=self.ROBOT_FRAMEWORK_XML_V5, get_request_json_return_value={})
        self.assert_measurement(response, value="7.1.1")

    async def test_newer_version(self):
        """Test that the Robot Framework version is returned, and a message that a new version is available."""
        response = await self.collect(
            get_request_text=self.ROBOT_FRAMEWORK_XML_V5, get_request_json_return_value={"tag_name": "7.1.2"}
        )
        self.assert_measurement(response, value="7.1.1", info_message="Latest available version is 7.1.2")
