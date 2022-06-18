"""Unit tests for the SonarQube source code version collector."""

from .base import SonarQubeTestCase


class SonarQubeSourceCodeVersionTest(SonarQubeTestCase):
    """Unit tests for the SonarQube source code version collector."""

    METRIC_TYPE = "source_code_version"
    METRIC_ADDITION = "min"

    async def test_source_code_version(self):
        """Test that the source code version is returned."""
        json = dict(analyses=[dict(projectVersion="1.2.1")])
        response = await self.collect(get_request_json_return_value=json)
        self.assert_measurement(
            response, value="1.2.1", landing_url="https://sonarqube/project/activity?id=id&branch=master"
        )
