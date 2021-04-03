"""Unit tests for the Axe-core source version collector."""

from .base import AxeCoreTestCase


class AxeCoreSourceVersionTest(AxeCoreTestCase):
    """Unit tests for the source version collector."""

    METRIC_TYPE = "source_version"
    METRIC_ADDITION = "min"

    async def test_source_version(self):
        """Test that the Axe-core version is returned."""
        axe_json = dict(testEngine=dict(version="4.1.3"))
        response = await self.collect(get_request_json_return_value=axe_json)
        self.assert_measurement(response, value="4.1.3")
