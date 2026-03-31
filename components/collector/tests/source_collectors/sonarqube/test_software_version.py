"""Unit tests for the SonarQube software version collector."""

from .base import SonarQubeTestCase


class SonarQubeSoftwareVersionTest(SonarQubeTestCase):
    """Unit tests for the SonarQube software version collector."""

    METRIC_TYPE = "software_version"

    async def test_software_version(self):
        """Test that the software version is returned."""
        json = {"analyses": [{"projectVersion": "1.2.1"}]}
        response = await self.collect(get_request_json_return_value=json)
        self.assert_measurement(
            response,
            value="1.2.1",
            landing_url="https://sonarqube/project/activity?id=id&branch=main",
        )

    async def test_non_semantic_version_with_pattern(self):
        """Test that a non-semantic version can be parsed with a version number pattern."""
        self.set_source_parameter("version_number_pattern", r"\d+")
        json = {"analyses": [{"projectVersion": "1115-code-coverage-SNAPSHOT"}]}
        response = await self.collect(get_request_json_return_value=json)
        self.assert_measurement(
            response,
            value="1115",
            landing_url="https://sonarqube/project/activity?id=id&branch=main",
        )

    async def test_non_semantic_version_without_pattern(self):
        """Test that a non-semantic version without pattern results in a parse error."""
        json = {"analyses": [{"projectVersion": "1115-code-coverage-SNAPSHOT"}]}
        response = await self.collect(get_request_json_return_value=json)
        self.assert_measurement(response, parse_error="Invalid version")

    async def test_non_semantic_version_with_non_matching_pattern(self):
        """Test that a non-semantic version with a non-matching pattern results in a parse error."""
        self.set_source_parameter("version_number_pattern", r"v\d+\.\d+\.\d+")
        json = {"analyses": [{"projectVersion": "1115-code-coverage-SNAPSHOT"}]}
        response = await self.collect(get_request_json_return_value=json)
        self.assert_measurement(response, parse_error="Invalid version")
