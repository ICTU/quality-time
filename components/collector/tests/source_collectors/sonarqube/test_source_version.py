"""Unit tests for the SonarQube source version collector."""

from .base import SonarQubeTestCase


class SonarQubeSourceVersionTest(SonarQubeTestCase):
    """Unit tests for the SonarQube source version collector."""

    METRIC_TYPE = "source_version"
    METRIC_ADDITION = "min"

    async def test_source_version(self):
        """Test that the SonarQube version number is returned."""
        response = await self.collect(get_request_text="8.6.0")
        self.assert_measurement(response, value="8.6.0", landing_url="https://sonarqube")
