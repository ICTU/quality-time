"""Unit tests for the Gatling source version collector."""

from .base import GatlingTestCase


class GatlingSourceVersionTest(GatlingTestCase):
    """Unit tests for the Gatling source version collector."""

    METRIC_TYPE = "source_version"

    async def test_source_version_missing(self):
        """Test that a dummy version is returned if the version cannot be found."""
        response = await self.collect(get_request_text="<span/>")
        self.assert_measurement(response, value="9999")

    async def test_source_version(self):
        """Test that the source version is returned."""
        response = await self.collect(
            get_request_text="""
<span class="simulation-information-item">
    <span class="simulation-information-label">Version: </span>
    <span>3.14.3</span>
</span>
"""
        )
        self.assert_measurement(response, value="3.14.3")
