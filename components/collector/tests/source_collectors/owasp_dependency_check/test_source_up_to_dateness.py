"""Unit tests for the OWASP Dependency Check source up-to-dateness collector."""

from datetime import datetime, timedelta, timezone

from collector_utilities.date_time import days_ago

from .base import OWASPDependencyCheckTestCase


class OWASPDependencyCheckTest(OWASPDependencyCheckTestCase):
    """Unit tests for the OWASP Dependency Check source up-to-dateness collector."""

    METRIC_TYPE = "source_up_to_dateness"

    async def test_source_up_to_dateness(self):
        """Test that the source age in days is returned."""
        response = await self.collect(get_request_text=self.xml)
        timezone_info = timezone(timedelta(hours=2))
        expected_age = days_ago(datetime(2018, 10, 3, 13, 1, 24, 784, tzinfo=timezone_info))
        self.assert_measurement(response, value=str(expected_age))
