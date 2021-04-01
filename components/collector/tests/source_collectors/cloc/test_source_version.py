"""Unit tests for the cloc source version collector."""

from ..source_collector_test_case import SourceCollectorTestCase


class ClocVersionTest(SourceCollectorTestCase):
    """Unit tests for the cloc source version collector."""

    SOURCE_TYPE = "cloc"
    METRIC_TYPE = "source_version"

    async def test_version(self):
        """Test that the source version is returned."""
        response = await self.collect(get_request_json_return_value=dict(header=dict(cloc_version="1.86")))
        self.assert_measurement(response, value=str("1.86"))
