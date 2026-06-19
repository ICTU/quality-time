"""Unit tests for the Dependency-Track security warnings collector."""

from typing import TYPE_CHECKING

from aiohttp import BasicAuth

from source_collectors.dependency_track.base import DependencyTrackBase
from source_collectors.dependency_track.security_warnings import (
    DependencyTrackComponent,
    DependencyTrackFinding,
    DependencyTrackVulnerability,
)

from .base_test import DependencyTrackTestCase

if TYPE_CHECKING:
    from model.measurement import MetricMeasurement
    from source_collectors.dependency_track.json_types import DependencyTrackProject


class DependencyTrackSecurityWarningsTest(DependencyTrackTestCase):
    """Unit tests for the Dependency-Track security warnings collector."""

    METRIC_TYPE = "security_warnings"

    def findings(
        self,
        description: str | None = "description",
        severity: str | None = "UNASSIGNED",
    ) -> list[DependencyTrackFinding]:
        """Create the Dependency-Track findings fixture. Pass None to omit the description or severity."""
        vulnerability = DependencyTrackVulnerability(vulnId="CVE-123")
        if description is not None:
            vulnerability["description"] = description
        if severity is not None:
            vulnerability["severity"] = severity
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
                vulnerability=vulnerability,
            ),
        ]

    def entities(self, description: str = "description", severity: str = "Unassigned") -> list[dict[str, str]]:
        """Create the expected entities."""
        return [
            {
                "component": "component name",
                "component_landing_url": f"{self.landing_url}/components/component-uuid",
                "description": description,
                "identifier": "CVE-123",
                "key": "matrix",
                "latest": "2",
                "latest_version_status": "update possible",
                "project": "project name",
                "project_landing_url": f"{self.landing_url}/projects/project uuid",
                "project_version": "1.4",
                "severity": severity,
                "version": "1",
            },
        ]

    async def collect_findings(
        self,
        projects: list[DependencyTrackProject] | None = None,
        findings: list[DependencyTrackFinding] | None = None,
    ) -> MetricMeasurement:
        """Collect a measurement for the given projects and findings, defaulting to the fixtures."""
        return await self.collect_measurement(
            get_request_json_side_effect=[
                self.projects() if projects is None else projects,
                self.findings() if findings is None else findings,
            ],
        )

    async def test_no_projects(self):
        """Test that an error is thrown if there are no projects."""
        measurement = await self.collect_measurement(get_request_json_return_value=[])
        self.assert_no_projects_found(measurement)

    async def test_one_project_without_vulnerabilities(self):
        """Test one project without vulnerabilities."""
        measurement = await self.collect_findings(findings=[])
        self.assert_measurement(measurement, value="0", entities=[])

    async def test_one_project_with_vulnerabilities(self):
        """Test one project with vulnerabilities."""
        measurement = await self.collect_findings()
        self.assert_measurement(measurement, value="1", entities=self.entities())

    async def test_vulnerability_without_description(self):
        """Test that a vulnerability without a description does not cause a failure."""
        measurement = await self.collect_findings(findings=self.findings(description=None))
        self.assert_measurement(measurement, value="1", entities=self.entities(description=""))

    async def test_vulnerability_without_severity(self):
        """Test that a vulnerability without a severity does not cause a failure."""
        measurement = await self.collect_findings(findings=self.findings(severity=None))
        self.assert_measurement(measurement, value="1", entities=self.entities())

    async def test_filter_by_severity(self):
        """Test that vulnerabilities can be filtered out by severity."""
        self.set_source_parameter("severities", ["High", "Critical"])
        measurement = await self.collect_findings()
        self.assert_measurement(measurement, value="0", entities=[])

    async def test_filter_by_matching_severity(self):
        """Test that vulnerabilities with a matching severity are included."""
        self.set_source_parameter("severities", ["High", "Critical"])
        measurement = await self.collect_findings(findings=self.findings(severity="HIGH"))
        self.assert_measurement(measurement, value="1", entities=self.entities(severity="High"))

    async def test_filter_by_project_name(self):
        """Test filtering projects by name."""
        self.set_source_parameter("project_names", ["project name"])
        measurement = await self.collect_findings()
        self.assert_measurement(measurement, value="1", entities=self.entities())

    async def test_filter_by_project_name_without_match(self):
        """Test filtering projects by name."""
        self.set_source_parameter("project_names", ["other project"])
        measurement = await self.collect_findings()
        self.assert_no_projects_found(measurement)

    async def test_filter_by_project_regular_expression(self):
        """Test filtering projects by regular expression."""
        self.set_source_parameter("project_names", ["project .*"])
        measurement = await self.collect_findings()
        self.assert_measurement(measurement, value="1", entities=self.entities())

    async def test_filter_by_project_version(self):
        """Test filtering projects by version."""
        self.set_source_parameter("project_versions", ["1.2", "1.3", "1.4"])
        measurement = await self.collect_findings()
        self.assert_measurement(measurement, value="1", entities=self.entities())

    async def test_filter_by_project_version_without_match(self):
        """Test filtering projects by version."""
        self.set_source_parameter("project_versions", ["1.2", "1.3"])
        measurement = await self.collect_findings()
        self.assert_no_projects_found(measurement)

    async def test_filter_by_project_name_and_version(self):
        """Test filtering projects by name and version."""
        self.set_source_parameter("project_names", ["project .*"])
        self.set_source_parameter("project_versions", ["1.3", "1.4"])
        measurement = await self.collect_findings()
        self.assert_measurement(measurement, value="1", entities=self.entities())

    async def test_filter_by_latest_project(self):
        """Test that projects can be filtered by being the latest project version."""
        self.set_source_parameter("only_include_latest_project_versions", "yes")
        measurement = await self.collect_findings(projects=self.projects(is_latest=True))
        self.assert_measurement(measurement, value="1", entities=self.entities())

    async def test_filter_by_latest_project_without_match(self):
        """Test that projects can be filtered by being the latest project version."""
        self.set_source_parameter("only_include_latest_project_versions", "yes")
        measurement = await self.collect_findings()
        self.assert_no_projects_found(measurement)

    async def test_include_by_component_name(self):
        """Test filtering by component name."""
        self.set_source_parameter("components_to_include", ["other component"])
        measurement = await self.collect_findings()
        self.assert_measurement(measurement, value="0", entities=[])

    async def test_include_by_component_name_regular_expression(self):
        """Test filtering by component name regular expression."""
        self.set_source_parameter("components_to_include", ["component.*"])
        measurement = await self.collect_findings()
        self.assert_measurement(measurement, value="1", entities=self.entities())

    async def test_exclude_by_component_name(self):
        """Test filtering by component name."""
        self.set_source_parameter("components_to_ignore", ["component name"])
        measurement = await self.collect_findings()
        self.assert_measurement(measurement, value="0", entities=[])

    async def test_exclude_by_component_name_regular_expression(self):
        """Test filtering by component name regular expression."""
        self.set_source_parameter("components_to_ignore", ["other.*"])
        measurement = await self.collect_findings()
        self.assert_measurement(measurement, value="1", entities=self.entities())

    async def test_api_key(self):
        """Test that the API key is passed as header."""
        self.set_source_parameter("private_token", "API key")
        _, get, _ = await self.collect_measurement_and_mocks(get_request_json_return_value=[])
        get.assert_called_once_with(
            f"https://dependency_track/api/v1/project?pageSize={DependencyTrackBase.PAGE_SIZE}&pageNumber=1",
            allow_redirects=True,
            auth=BasicAuth(login="API key", password="", encoding="latin1"),  # nosec
            headers={"X-Api-Key": "API key"},
        )
