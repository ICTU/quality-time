"""Unit tests for the Robot Framework XML test report source."""

from datetime import datetime

from .base import RobotFrameworkTestCase


class RobotFrameworkSourceUpToDatenessTest(RobotFrameworkTestCase):
    """Unit test for the source up-to-dateness metric."""

    METRIC_TYPE = "source_up_to_dateness"
    METRIC_ADDITION = "max"

    async def test_source_up_to_dateness(self):
        """Test that the source age in days is returned."""
        xml = """<?xml version="1.0"?><robot generated="2009-12-19T17:58:59"/>"""
        response = await self.collect(get_request_text=xml)
        expected_age = (datetime.now() - datetime(2009, 12, 19, 17, 58, 59)).days
        self.assert_measurement(response, value=str(expected_age))
