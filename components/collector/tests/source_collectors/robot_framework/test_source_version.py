"""Unit tests for the Robot Framework source version collector."""

from .base import RobotFrameworkTestCase


class RobotFrameworkSourceVersion(RobotFrameworkTestCase):
    """Unit test for the source version metric."""

    METRIC_TYPE = "source_version"
    METRIC_ADDITION = "min"

    async def test_source_version(self):
        """Test that the Robot Framework version is returned."""
        xml = """<?xml version="1.0"?><robot generator="Robot 3.1.1 (Python 3.7.0 on darwin)"/>"""
        response = await self.collect(get_request_text=xml)
        self.assert_measurement(response, value="3.1.1")
