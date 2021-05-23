"""Unit tests for the Robot Framework source version collector."""

from .base import RobotFrameworkTestCase


class RobotFrameworkSourceVersion(RobotFrameworkTestCase):
    """Unit test for the source version metric."""

    METRIC_TYPE = "source_version"
    METRIC_ADDITION = "min"

    async def test_source_version3(self):
        """Test that the Robot Framework version is returned."""
        response = await self.collect(get_request_text=self.ROBOT_FRAMEWORK_XML_V3)
        self.assert_measurement(response, value="3.2.2")

    async def test_source_version4(self):
        """Test that the Robot Framework version is returned."""
        response = await self.collect(get_request_text=self.ROBOT_FRAMEWORK_XML_V4)
        self.assert_measurement(response, value="4.0b3.dev1")
