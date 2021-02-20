"""Unit tests for the NCover source."""

from datetime import datetime

from .base import NCoverTestCase


class NCoverSourceUpToDatenessTest(NCoverTestCase):
    """Unit tests for the NCover source up-to-dateness collector."""

    METRIC_TYPE = "source_up_to_dateness"
    NCOVER_HTML = """
         <script type="text/javascript">
            ncover.serverRoot = 'https://127.0.0.1:11235';
            ncover.createDateTime = '1440425155042';
        </script>"""

    async def test_source_up_to_dateness(self):
        """Test that the source age in days is returned."""
        response = await self.collect(self.metric, get_request_text=self.NCOVER_HTML)
        report_datetime = datetime.fromtimestamp(1440425155042 / 1000.0)
        expected_age = (datetime.now(tz=report_datetime.tzinfo) - report_datetime).days
        self.assert_measurement(response, value=str(expected_age))
