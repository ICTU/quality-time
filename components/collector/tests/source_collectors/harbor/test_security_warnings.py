"""Unit tests for the Harbor security warnings collector."""

import aiohttp

from tests.source_collectors.source_collector_test_case import SourceCollectorTestCase


class FakeResponse:
    """Fake GitLab response."""

    def __init__(self, fake_json) -> None:
        self.fake_json = fake_json
        self.links: dict[str, dict[str, str]] = {}

    async def json(self):
        """Return the fake JSON."""
        return self.fake_json


class HarborSecurityWarningsTest(SourceCollectorTestCase):
    """Unit tests for the Harbor security warnings collector."""

    METRIC_TYPE = "security_warnings"
    SOURCE_TYPE = "harbor"

    PROJECT_NAME = "docker.io"
    REPO_NAME = f"{PROJECT_NAME}/repo"
    SCAN_REPORT_MIME_TYPE = "application/vnd.security.vulnerability.report; version=1.1"

    def setUp(self) -> None:
        """Set up test fixtures."""
        super().setUp()
        self.expected_entity = {
            "artifact": "sha256:43f789166",
            "fixable": "0",
            "highest_severity": "Unknown",
            "key": "sha256:43f7891666042ef31c08d6e7fefc68bd0e98545cdd2dfa846b23d3fd9d71cb2e",
            "project": self.PROJECT_NAME,
            "repository": "tianon/postgres-upgrade",
            "tags": "",
            "total": "1",
            "url": (
                "https://harbor/harbor/projects/3/repositories/tianon%2Fpostgres-upgrade/artifacts-tab/artifacts/"
                "sha256:43f7891666042ef31c08d6e7fefc68bd0e98545cdd2dfa846b23d3fd9d71cb2e"
            ),
        }

    async def collect_data(self):
        """Collect the (fake) Harbor contents."""
        project = self.PROJECT_NAME
        return await self.collect(
            get_request_json_side_effect=[
                [{"name": project}],
                [{"name": self.REPO_NAME}],
                [
                    {
                        "addition_links": {
                            "vulnerabilities": {
                                "href": f"/api/v2.0/projects/{project}/repositories/tianon%252Fpostgres-upgrade/"
                                "artifacts/sha256: 43f7891666042ef31c08d6e7fefc68bd0e98545cdd2dfa846b23d3fd9d71cb2e/"
                                "additions/vulnerabilities",
                            },
                        },
                        "digest": "sha256: 43f7891666042ef31c08d6e7fefc68bd0e98545cdd2dfa846b23d3fd9d71cb2e",
                        "project_id": 3,
                        "scan_overview": {
                            self.SCAN_REPORT_MIME_TYPE: {"scan_status": "Success", "summary": {"total": 1}},
                        },
                    },
                ],
            ],
        )

    async def test_invalid_credentials(self):
        """Test that invalid credentials result in an error."""
        self.set_source_parameter("username", "user")
        self.set_source_parameter("password", "invalid")
        response = await self.collect(get_request_json_side_effect=aiohttp.ClientError)
        self.assert_measurement(response, connection_error="ClientError")

    async def test_credentials_test_is_skipped_for_robot_users(self):
        """Test that the credentials test is skipped for robot users."""
        self.set_source_parameter("username", "robot_user")
        self.set_source_parameter("password", "invalid")
        response = await self.collect(get_request_side_effect=[FakeResponse({})])
        self.assert_measurement(response, value="0", entities=[])

    async def test_no_projects(self):
        """Test that there are no security warnings if there are no projects."""
        response = await self.collect(get_request_json_return_value=[])
        self.assert_measurement(response, value="0", entities=[])

    async def test_no_repositories(self):
        """Test that there are no security warnings if there are no repositories."""
        response = await self.collect(get_request_json_side_effect=[[{"name": self.PROJECT_NAME}], []])
        self.assert_measurement(response, value="0", entities=[])

    async def test_no_artifacts(self):
        """Test that there are no security warnings if there are no artifacts."""
        response = await self.collect(
            get_request_json_side_effect=[[{"name": self.PROJECT_NAME}], [{"name": self.REPO_NAME}], []],
        )
        self.assert_measurement(response, value="0", entities=[])

    async def test_no_scans(self):
        """Test that there are no security warnings if there are no scans."""
        response = await self.collect(
            get_request_json_side_effect=[[{"name": self.PROJECT_NAME}], [{"name": self.REPO_NAME}], [{}]],
        )
        self.assert_measurement(response, value="0", entities=[])

    async def test_scan_status_not_successful(self):
        """Test that there are no security warnings if the scan is not successful."""
        response = await self.collect(
            get_request_json_side_effect=[
                [{"name": self.PROJECT_NAME}],
                [{"name": self.REPO_NAME}],
                [{"scan_overview": {self.SCAN_REPORT_MIME_TYPE: {}}}],
            ],
        )
        self.assert_measurement(response, value="0", entities=[])

    async def test_scan_overview_has_unknown_report(self):
        """Test that an exception is thrown if the scan report format is not recognized."""
        response = await self.collect(
            get_request_json_side_effect=[
                [{"name": self.PROJECT_NAME}],
                [{"name": self.REPO_NAME}],
                [{"scan_overview": {"unknown_format": {}}}],
            ],
        )
        self.assert_measurement(response, parse_error="Harbor scanner vulnerability report contains no known format")

    async def test_scan_without_warnings(self):
        """Test that there are no security warnings if the scan has no warnings."""
        response = await self.collect(
            get_request_json_side_effect=[
                [{"name": self.PROJECT_NAME}],
                [{"name": self.REPO_NAME}],
                [{"scan_overview": {self.SCAN_REPORT_MIME_TYPE: {"scan_status": "Success", "summary": {}}}}],
            ],
        )
        self.assert_measurement(response, value="0", entities=[])

    async def test_scan_with_warnings(self):
        """Test that there are security warnings if the scan has warnings."""
        response = await self.collect_data()
        self.assert_measurement(response, value="1", entities=[self.expected_entity])

    async def test_filter_severity_match(self):
        """Test that the security warnings can be filtered by severity."""
        self.set_source_parameter("severities", ["unknown"])
        response = await self.collect_data()
        self.assert_measurement(response, value="1", entities=[self.expected_entity])

    async def test_filter_severity_no_match(self):
        """Test that the security warnings can be filtered by severity."""
        self.set_source_parameter("severities", ["high"])
        response = await self.collect_data()
        self.assert_measurement(response, value="0", entities=[])

    async def test_fix_available(self):
        """Test that the security warnings can be filtered by fix availability."""
        self.set_source_parameter("fix_availability", ["fix available"])
        response = await self.collect_data()
        self.assert_measurement(response, value="0", entities=[])

    async def test_fix_not_available(self):
        """Test that the security warnings can be filtered by fix availability."""
        self.set_source_parameter("fix_availability", ["no fix available"])
        response = await self.collect_data()
        self.assert_measurement(response, value="1", entities=[self.expected_entity])

    async def test_pagination(self):
        """Test that pagination works."""
        links = {"next": {"url": "https://harbor/next_page"}}
        response = await self.collect(get_request_links=links, get_request_json_side_effect=[[], []])
        self.assert_measurement(response, value="0", entities=[])

    async def test_ignore_project(self):
        """Test that a project can be ignored."""
        self.set_source_parameter("projects_to_ignore", self.PROJECT_NAME)
        response = await self.collect_data()
        self.assert_measurement(response, value="0", entities=[])

    async def test_include_project(self):
        """Test that a project can be included."""
        self.set_source_parameter("projects_to_include", "other_project")
        response = await self.collect_data()
        self.assert_measurement(response, value="0", entities=[])

    async def test_ignore_repository(self):
        """Test that a repository can be ignored."""
        self.set_source_parameter("repositories_to_ignore", self.REPO_NAME)
        response = await self.collect_data()
        self.assert_measurement(response, value="0", entities=[])

    async def test_include_repository(self):
        """Test that a repository can be included."""
        self.set_source_parameter("repositories_to_include", "other_repo")
        response = await self.collect_data()
        self.assert_measurement(response, value="0", entities=[])
