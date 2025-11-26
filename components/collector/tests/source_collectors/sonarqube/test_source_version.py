"""Unit tests for the SonarQube source version collector."""

from .base import SonarQubeTestCase


class SonarQubeSourceVersionTest(SonarQubeTestCase):
    """Unit tests for the SonarQube source version collector."""

    METRIC_TYPE = "source_version"

    async def test_source_version(self):
        """Test that the SonarQube version number is returned."""
        response = await self.collect(get_request_text="2025.2.0.105476")
        self.assert_measurement(response, value="2025.2.0.105476", landing_url="https://sonarqube")
