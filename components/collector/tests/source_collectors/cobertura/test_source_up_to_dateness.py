"""Unit tests for the Cobertura source up-to-dateness collector."""

from datetime import datetime

from dateutil.tz import tzutc

from .base import CoberturaTestCase


class CoberturaSourceUpToDatenessTest(CoberturaTestCase):
    """Unit tests for the Cobertura source up-to-dateness collector."""

    METRIC_TYPE = "source_up_to_dateness"

    def setUp(self):
        """Extend to compute the expected age of the Cobertura report."""
        super().setUp()
        self.expected_age = str((datetime.now(tz=tzutc()) - datetime.fromtimestamp(1553821197.442, tz=tzutc())).days)

    def cobertura_xml(self, timestamp: str | None = "1553821197442") -> str:
        """Create the Cobertura XML."""
        return "<coverage />" if timestamp is None else f'<coverage timestamp="{timestamp}" />'

    async def test_source_up_to_dateness(self):
        """Test that the source age in days is returned."""
        response = await self.collect(get_request_text=self.cobertura_xml())
        self.assert_measurement(response, value=self.expected_age)

    async def test_source_up_to_dateness_with_timestamp_in_seconds(self):
        """Test that the source age in days is returned."""
        timestamp = 1553821197
        response = await self.collect(get_request_text=self.cobertura_xml(timestamp=str(timestamp)))
        self.assert_measurement(response, value=self.expected_age)
        timestamp -= 24 * 60 * 60  # One day older
        response = await self.collect(get_request_text=self.cobertura_xml(timestamp=str(timestamp)))
        self.assert_measurement(response, value=str(int(self.expected_age) + 1))

    async def test_zipped_report(self):
        """Test that a zipped report can be read."""
        self.set_source_parameter("url", "https://example.org/cobertura.zip")
        response = await self.collect(get_request_content=self.zipped_report(("cobertura.xml", self.cobertura_xml())))
        self.assert_measurement(response, value=self.expected_age)

    async def test_missing_timestamp(self):
        """Test that an exception is thrown when the timestamp is missing."""
        response = await self.collect(get_request_text=self.cobertura_xml(timestamp=None))
        self.assert_measurement(response, parse_error="Cobertura XML tag 'timestamp' not found")
