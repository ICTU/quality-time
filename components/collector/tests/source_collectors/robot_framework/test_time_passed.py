"""Unit tests for the Robot Framework XML test report time passed collector."""

from datetime import datetime

from .base import RobotFrameworkTestCase


class RobotFrameworkTimePassedTest(RobotFrameworkTestCase):
    """Unit test for the time passed collector."""

    METRIC_TYPE = "time_passed"
    METRIC_ADDITION = "max"

    async def test_time_passed(self):
        """Test that the source age in days is returned."""
        for xml in [self.ROBOT_FRAMEWORK_XML_V3, self.ROBOT_FRAMEWORK_XML_V4]:
            with self.subTest(xml=xml):
                response = await self.collect(get_request_text=xml)
                expected_age = (datetime.now() - datetime(2021, 2, 12, 17, 27, 3)).days
                self.assert_measurement(response, value=str(expected_age))
