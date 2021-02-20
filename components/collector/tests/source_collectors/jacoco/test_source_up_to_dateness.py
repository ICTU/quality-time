"""Unit tests for the JaCoCo source up-to-dateness collector."""

from datetime import datetime

from .base import JaCoCoCommonTestsMixin, JaCoCoTestCase


class JaCoCoSourceUpToDatenessTest(JaCoCoCommonTestsMixin, JaCoCoTestCase):
    """Unit tests for the JaCoCo source up-to-dateness collector."""

    METRIC_TYPE = "source_up_to_dateness"
    METRIC_ADDITION = "max"
    JACOCO_XML = '<report><sessioninfo dump="1553821197442"/></report>'

    def setUp(self):
        """Extend to set up a common source for the tests."""
        super().setUp()
        self.expected_age = (datetime.utcnow() - datetime.utcfromtimestamp(1553821197.442)).days

    async def test_source_up_to_dateness(self):
        """Test that the source age in days is returned."""
        response = await self.collect(get_request_text=self.JACOCO_XML)
        self.assert_measurement(response, value=str(self.expected_age))

    async def test_zipped_report(self):
        """Test that a zipped report can be read."""
        self.set_source_parameter("url", "https://jacoco.zip")
        response = await self.collect(get_request_content=self.zipped_report(("jacoco.xml", self.JACOCO_XML)))
        self.assert_measurement(response, value=str(self.expected_age))
