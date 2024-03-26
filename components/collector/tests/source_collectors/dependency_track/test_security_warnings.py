"""Unit tests for the Dependency-Track security warnings collector."""

from aiohttp import BasicAuth

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class DependencyTrackSecurityWarningsTest(SourceCollectorTestCase):
    """Unit tests for the Dependency-Track security warnings collector."""

    METRIC_TYPE = "security_warnings"
    SOURCE_TYPE = "dependency_track"

    def setUp(self) -> None:
        """Extend to set up Dependency-Track responses and expected measurement entities."""
        super().setUp()
        self.projects = [{"uuid": "project uuid", "name": "project name"}]
        self.vulnerabilities = [
            {
                "component": {"name": "component name", "project": "project uuid", "uuid": "component-uuid"},
                "matrix": "matrix",
                "vulnerability": {
                    "description": "vulnerability description",
                    "severity": "UNASSIGNED",
                    "vulnId": "CVE-123",
                },
            },
        ]
        self.entities = [
            {
                "component": "component name",
                "component_landing_url": "/components/component-uuid",
                "description": "vulnerability description",
                "identifier": "CVE-123",
                "key": "matrix",
                "project": "project name",
                "project_landing_url": "/projects/project uuid",
                "severity": "Unassigned",
            },
        ]

    async def test_no_projects(self):
        """Test that there are no security warnings if there are no projects."""
        response = await self.collect(get_request_json_return_value=[])
        self.assert_measurement(response, value="0", entities=[])

    async def test_one_project_without_vulnerabilities(self):
        """Test one project without vulnerabilities."""
        response = await self.collect(get_request_json_side_effect=[self.projects, []])
        self.assert_measurement(response, value="0", entities=[])

    async def test_one_project_with_vulnerabilities(self):
        """Test one project with vulnerabilities."""
        response = await self.collect(get_request_json_side_effect=[self.projects, self.vulnerabilities])
        self.assert_measurement(response, value="1", entities=self.entities)

    async def test_filter_vulnerabilities(self):
        """Test that vulnerabilities can be filtered."""
        self.set_source_parameter("severities", ["High", "Critical"])
        response = await self.collect(get_request_json_side_effect=[self.projects, self.vulnerabilities])
        self.assert_measurement(response, value="0", entities=[])

    async def test_api_key(self):
        """Test that the API key is passed as header."""
        self.set_source_parameter("private_token", "API key")
        _, get, _ = await self.collect(get_request_json_return_value=[], return_mocks=True)
        get.assert_called_once_with(
            "https://dependency_track/api/v1/project?pageSize=25&pageNumber=1",
            allow_redirects=True,
            auth=BasicAuth(login="API key", password="", encoding="latin1"),
            headers={"X-Api-Key": "API key"},
        )
