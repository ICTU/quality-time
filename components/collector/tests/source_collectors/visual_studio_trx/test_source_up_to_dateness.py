"""Unit tests for the Visual Studio TRX test report source up-to-dateness collector."""

from collector_utilities.date_time import days_ago, parse_datetime

from .base import VisualStudioTRXCollectorTestCase


class VisualStudioTRXSourceUpToDatenessTest(VisualStudioTRXCollectorTestCase):
    """Unit tests for the source up-to-dateness collector."""

    METRIC_TYPE = "source_up_to_dateness"

    async def test_source_up_to_dateness(self):
        """Test that the source age in days is returned."""
        response = await self.collect(get_request_text=self.VISUAL_STUDIO_TRX_XML)
        expected_age = days_ago(parse_datetime("2024-09-12T11:33:30.3272909+02:00"))
        self.assert_measurement(response, value=str(expected_age))
