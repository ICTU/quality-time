"""Unit tests for the SonarQube software version collector."""

from .base import SonarQubeTestCase


class SonarQubeSoftwareVersionTest(SonarQubeTestCase):
    """Unit tests for the SonarQube software version collector."""

    METRIC_TYPE = "software_version"
    METRIC_ADDITION = "min"

    async def test_software_version(self):
        """Test that the software version is returned."""
        json = dict(analyses=[dict(projectVersion="1.2.1")])
        response = await self.collect(get_request_json_return_value=json)
        self.assert_measurement(
            response, value="1.2.1", landing_url="https://sonarqube/project/activity?id=id&branch=master"
        )
