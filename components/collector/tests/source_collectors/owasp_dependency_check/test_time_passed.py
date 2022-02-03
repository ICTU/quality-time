"""Unit tests for the OWASP Dependency Check time passed collector."""

from datetime import datetime, timedelta, timezone

from .base import OWASPDependencyCheckTestCase


class OWASPDependencyCheckTimePassedTest(OWASPDependencyCheckTestCase):
    """Unit tests for the OWASP Dependency Check time passed collector."""

    METRIC_TYPE = "time_passed"

    async def test_time_passed(self):
        """Test that the source age in days is returned."""
        response = await self.collect(get_request_text=self.xml)
        timezone_info = timezone(timedelta(hours=2))
        expected_age = (datetime.now(timezone_info) - datetime(2018, 10, 3, 13, 1, 24, 784, tzinfo=timezone_info)).days
        self.assert_measurement(response, value=str(expected_age))
