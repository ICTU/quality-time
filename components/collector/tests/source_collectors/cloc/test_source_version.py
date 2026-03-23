"""Unit tests for the cloc source version collector."""

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class ClocVersionTest(SourceCollectorTestCase):
    """Unit tests for the cloc source version collector."""

    SOURCE_TYPE = "cloc"
    METRIC_TYPE = "source_version"

    async def test_version(self):
        """Test that the source version is returned."""
        response = await self.collect(get_request_json_return_value={"header": {"cloc_version": "1.86"}})
        self.assert_measurement(response, value="1.86")

    async def test_newer_version_available(self):
        """Test that the source version is returned, including a message that a newer version is available."""
        response = await self.collect(
            get_request_json_return_value={"tag_name": "1.87", "header": {"cloc_version": "1.86"}}
        )
        self.assert_measurement(response, value="1.86", info_message="Latest available version is 1.87")
