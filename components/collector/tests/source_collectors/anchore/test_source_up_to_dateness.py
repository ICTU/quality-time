"""Unit tests for the Anchore source up-to-dateness collector."""

import io
import json
import zipfile
from datetime import datetime, timezone

from .base import AnchoreTestCase


class AnchoreSourceUpToDatenessTest(AnchoreTestCase):
    """Unit tests for the source up-to-dateness collector."""

    METRIC_TYPE = "source_up_to_dateness"
    METRIC_ADDITION = "max"

    def setUp(self):
        """Extend to set up test data."""
        super().setUp()
        self.expected_age = (datetime.now(tz=timezone.utc) - datetime(2020, 2, 7, 22, 53, 43, tzinfo=timezone.utc)).days

    async def test_source_up_to_dateness(self):
        """Test that the source age in days is returned."""
        response = await self.collect(self.metric, get_request_json_return_value=self.details_json)
        self.assert_measurement(response, value=str(self.expected_age))

    async def test_zipped_report(self):
        """Test that a zip with reports can be read."""
        self.set_source_parameter("details_url", "anchore.zip")
        bytes_io = io.BytesIO()
        with zipfile.ZipFile(bytes_io, mode="w") as zipped_anchore_report:
            zipped_anchore_report.writestr("vulnerabilities.json", json.dumps(self.vulnerabilities_json))
            zipped_anchore_report.writestr("details.json", json.dumps(self.details_json))
        response = await self.collect(self.metric, get_request_content=bytes_io.getvalue())
        self.assert_measurement(response, value=str(self.expected_age))
