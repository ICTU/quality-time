"""Unit tests for the Robot Framework XML test report source."""

from collector_utilities.date_time import datetime_fromparts, days_ago

from .base import RobotFrameworkTestCase


class RobotFrameworkSourceUpToDatenessTest(RobotFrameworkTestCase):
    """Unit test for the source up-to-dateness metric."""

    METRIC_TYPE = "source_up_to_dateness"
    METRIC_ADDITION = "max"

    async def test_source_up_to_dateness(self):
        """Test that the source age in days is returned."""
        for xml in [self.ROBOT_FRAMEWORK_XML_V3, self.ROBOT_FRAMEWORK_XML_V4]:
            with self.subTest(xml=xml):
                response = await self.collect(get_request_text=xml)
                expected_age = days_ago(datetime_fromparts(2021, 2, 12, 17, 27, 3))
                self.assert_measurement(response, value=str(expected_age))
