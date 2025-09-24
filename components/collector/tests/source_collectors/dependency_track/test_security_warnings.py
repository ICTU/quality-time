"""Unit tests for the Dependency-Track security warnings collector."""

from aiohttp import BasicAuth

from source_collectors.dependency_track.base import DependencyTrackBase
from source_collectors.dependency_track.security_warnings import (
    DependencyTrackComponent,
    DependencyTrackFinding,
    DependencyTrackVulnerability,
)

from .base_test import DependencyTrackTestCase


class DependencyTrackSecurityWarningsTest(DependencyTrackTestCase):
    """Unit tests for the Dependency-Track security warnings collector."""

    METRIC_TYPE = "security_warnings"

    def findings(self) -> list[DependencyTrackFinding]:
        """Create the Dependency-Track findings fixture."""
        return [
            DependencyTrackFinding(
                component=DependencyTrackComponent(
                    latestVersion="2",
                    name="component name",
                    project="project uuid",
                    uuid="component-uuid",
                    version="1",
                ),
                matrix="matrix",
                vulnerability=DependencyTrackVulnerability(
                    description="vulnerability description",
                    severity="UNASSIGNED",
                    vulnId="CVE-123",
                ),
            ),
        ]

    def entities(self) -> list[dict[str, str]]:
        """Create the expected entities."""
        return [
            {
                "component": "component name",
                "component_landing_url": f"{self.landing_url}/components/component-uuid",
                "description": "vulnerability description",
                "identifier": "CVE-123",
                "key": "matrix",
                "latest": "2",
                "latest_version_status": "update possible",
                "project": "project name",
                "project_landing_url": f"{self.landing_url}/projects/project uuid",
                "project_version": "1.4",
                "severity": "Unassigned",
                "version": "1",
            },
        ]

    async def test_no_projects(self):
        """Test that there are no security warnings if there are no projects."""
        response = await self.collect(get_request_json_return_value=[])
        self.assert_measurement(response, value="0", entities=[])

    async def test_one_project_without_vulnerabilities(self):
        """Test one project without vulnerabilities."""
        response = await self.collect(get_request_json_side_effect=[self.projects(), []])
        self.assert_measurement(response, value="0", entities=[])

    async def test_one_project_with_vulnerabilities(self):
        """Test one project with vulnerabilities."""
        response = await self.collect(get_request_json_side_effect=[self.projects(), self.findings()])
        self.assert_measurement(response, value="1", entities=self.entities())

    async def test_filter_by_severity(self):
        """Test that vulnerabilities can be filtered."""
        self.set_source_parameter("severities", ["High", "Critical"])
        response = await self.collect(get_request_json_side_effect=[self.projects(), self.findings()])
        self.assert_measurement(response, value="0", entities=[])

    async def test_filter_by_project_name(self):
        """Test filtering projects by name."""
        self.set_source_parameter("project_names", ["other project"])
        response = await self.collect(get_request_json_side_effect=[self.projects(), self.findings()])
        self.assert_measurement(response, value="0", entities=[])

    async def test_filter_by_project_regular_expression(self):
        """Test filtering projects by regular expression."""
        self.set_source_parameter("project_names", ["project .*"])
        response = await self.collect(get_request_json_side_effect=[self.projects(), self.findings()])
        self.assert_measurement(response, value="1", entities=self.entities())

    async def test_filter_by_project_version(self):
        """Test filtering projects by version."""
        self.set_source_parameter("project_versions", ["1.2", "1.3"])
        response = await self.collect(get_request_json_side_effect=[self.projects(), self.findings()])
        self.assert_measurement(response, value="0", entities=[])

    async def test_filter_by_project_name_and_version(self):
        """Test filtering projects by name and version."""
        self.set_source_parameter("project_names", ["project .*"])
        self.set_source_parameter("project_versions", ["1.3", "1.4"])
        response = await self.collect(get_request_json_side_effect=[self.projects(), self.findings()])
        self.assert_measurement(response, value="1", entities=self.entities())

    async def test_filter_by_latest_project(self):
        """Test that projects can be filtered by being the latest project version."""
        self.set_source_parameter("only_include_latest_project_versions", "yes")
        response = await self.collect(get_request_json_side_effect=[self.projects()])
        self.assert_measurement(response, value="0", entities=[])

    async def test_include_by_component_name(self):
        """Test filtering by component name."""
        self.set_source_parameter("components_to_include", ["other component"])
        response = await self.collect(get_request_json_side_effect=[self.projects(), self.findings()])
        self.assert_measurement(response, value="0", entities=[])

    async def test_include_by_component_name_regular_expression(self):
        """Test filtering by component name regular expression."""
        self.set_source_parameter("components_to_include", ["component.*"])
        response = await self.collect(get_request_json_side_effect=[self.projects(), self.findings()])
        self.assert_measurement(response, value="1", entities=self.entities())

    async def test_exclude_by_component_name(self):
        """Test filtering by component name."""
        self.set_source_parameter("components_to_ignore", ["component name"])
        response = await self.collect(get_request_json_side_effect=[self.projects(), self.findings()])
        self.assert_measurement(response, value="0", entities=[])

    async def test_exclude_by_component_name_regular_expression(self):
        """Test filtering by component name regular expression."""
        self.set_source_parameter("components_to_ignore", ["other.*"])
        response = await self.collect(get_request_json_side_effect=[self.projects(), self.findings()])
        self.assert_measurement(response, value="1", entities=self.entities())

    async def test_api_key(self):
        """Test that the API key is passed as header."""
        self.set_source_parameter("private_token", "API key")
        _, get, _ = await self.collect(get_request_json_return_value=[], return_mocks=True)
        get.assert_called_once_with(
            f"https://dependency_track/api/v1/project?pageSize={DependencyTrackBase.PAGE_SIZE}&pageNumber=1",
            allow_redirects=True,
            auth=BasicAuth(login="API key", password="", encoding="latin1"),  # nosec
            headers={"X-Api-Key": "API key"},
        )
