"""Unit tests for the GitLab inactive branches collector."""

from datetime import datetime
from http import HTTPStatus

import aiohttp
import multidict
import yarl
from dateutil.tz import tzutc

from .base import FakeResponse, GitLabTestCase


class GitLabInactiveBranchesTest(GitLabTestCase):
    """Unit tests for the inactive branches metric."""

    METRIC_TYPE = "inactive_branches"
    WEB_URL = "https://gitlab/namespace/project/-/tree/branch"

    def setUp(self):
        """Extend to setup fixtures."""
        super().setUp()
        self.set_source_parameter("project_or_group", "namespace/project")
        self.set_source_parameter("branches_to_ignore", ["ignored_.*"])
        main = self.create_branch("main", default=True)
        unmerged = self.create_branch("unmerged_branch")
        ignored = self.create_branch("ignored_branch")
        active_unmerged = self.create_branch("active_unmerged_branch", active=True)
        recently_merged = self.create_branch("merged_branch", merged=True, active=True)
        inactive_merged = self.create_branch("merged_branch", merged=True)
        self.branches = [main, unmerged, ignored, active_unmerged, recently_merged, inactive_merged]
        self.unmerged_branch_entity = self.create_entity("unmerged_branch", merged=False)
        self.merged_branch_entity = self.create_entity("merged_branch", merged=True)
        self.entities = [self.unmerged_branch_entity, self.merged_branch_entity]
        self.group_landing_url = "https://gitlab/namespace/project"
        self.project_landing_url = self.group_landing_url + "/-/branches"

    @staticmethod
    def response_error(status: HTTPStatus = HTTPStatus.NOT_FOUND) -> aiohttp.ClientResponseError:
        """Create a fake client response error."""
        request_info = aiohttp.RequestInfo(yarl.URL(), "", multidict.CIMultiDictProxy(multidict.CIMultiDict()))
        return aiohttp.ClientResponseError(request_info, (), status=status)

    @classmethod
    def group_does_not_exist(cls) -> aiohttp.ClientResponseError:
        """Return the response for an non-existing group."""
        return cls.response_error()

    @staticmethod
    def group_exists() -> FakeResponse:
        """Return the response for an existing group."""
        return FakeResponse({})

    @staticmethod
    def group_projects() -> FakeResponse:
        """Return a fake response with the projects of a group."""
        return FakeResponse([{"path_with_namespace": "group/project"}])

    def create_branch(
        self, name: str, *, default: bool = False, merged: bool = False, active: bool = False
    ) -> dict[str, str | bool | dict[str, str]]:
        """Create a GitLab branch."""
        commit_date = datetime.now(tz=tzutc()).isoformat() if active else "2019-04-02T11:33:04.000+02:00"
        return {
            "name": name,
            "default": default,
            "merged": merged,
            "web_url": self.WEB_URL,
            "commit": {"committed_date": commit_date},
        }

    def create_entity(self, name: str, *, merged: bool) -> dict[str, str]:
        """Create an entity."""
        return {
            "key": name,
            "name": name,
            "commit_date": "2019-04-02",
            "merge_status": "merged" if merged else "unmerged",
            "url": self.WEB_URL,
        }

    async def test_project_inactive_branches(self):
        """Test that the number of inactive branches of a project can be measured."""
        responses = [self.group_does_not_exist(), FakeResponse(self.branches), self.group_does_not_exist()]
        measurement = await self.collect(get_request_side_effect=responses)
        self.assert_measurement(measurement, value="2", entities=self.entities, landing_url=self.project_landing_url)

    async def test_group_inactive_branches(self):
        """Test that the number of inactive branches of a group of projects can be measured."""
        responses = [self.group_exists(), self.group_projects(), FakeResponse(self.branches), self.group_exists()]
        measurement = await self.collect(get_request_side_effect=responses)
        self.assert_measurement(measurement, value="2", entities=self.entities, landing_url=self.group_landing_url)

    async def test_project_unmerged_inactive_branches(self):
        """Test that the number of unmerged inactive branches of a project can be measured."""
        self.set_source_parameter("branch_merge_status", ["unmerged"])
        responses = [self.group_does_not_exist(), FakeResponse(self.branches), self.group_does_not_exist()]
        measurement = await self.collect(get_request_side_effect=responses)
        self.assert_measurement(
            measurement, value="1", entities=[self.unmerged_branch_entity], landing_url=self.project_landing_url
        )

    async def test_group_unmerged_inactive_branches(self):
        """Test that the number of unmerged inactive branches of a group of projects can be measured."""
        self.set_source_parameter("branch_merge_status", ["unmerged"])
        responses = [self.group_exists(), self.group_projects(), FakeResponse(self.branches), self.group_exists()]
        measurement = await self.collect(get_request_side_effect=responses)
        self.assert_measurement(
            measurement, value="1", entities=[self.unmerged_branch_entity], landing_url=self.group_landing_url
        )

    async def test_project_merged_inactive_branches(self):
        """Test that the number of merged inactive branches of a project can be measured."""
        self.set_source_parameter("branch_merge_status", ["merged"])
        responses = [self.group_does_not_exist(), FakeResponse(self.branches), self.group_does_not_exist()]
        measurement = await self.collect(get_request_side_effect=responses)
        self.assert_measurement(
            measurement, value="1", entities=[self.merged_branch_entity], landing_url=self.project_landing_url
        )

    async def test_group_merged_inactive_branches(self):
        """Test that the number of merged inactive branches of a group of projects can be measured."""
        self.set_source_parameter("branch_merge_status", ["merged"])
        responses = [self.group_exists(), self.group_projects(), FakeResponse(self.branches), self.group_exists()]
        measurement = await self.collect(get_request_side_effect=responses)
        self.assert_measurement(
            measurement, value="1", entities=[self.merged_branch_entity], landing_url=self.group_landing_url
        )

    async def test_project_pagination(self):
        """Test that pagination works when getting the branches of a project."""
        page1 = FakeResponse(self.branches[:3], links={"next": {"url": "https://gitlab/next_page"}})
        page2 = FakeResponse(self.branches[3:])
        responses = [self.group_does_not_exist(), page1, page2, self.group_does_not_exist()]
        measurement = await self.collect(get_request_side_effect=responses)
        self.assert_measurement(measurement, value="2", entities=self.entities, landing_url=self.project_landing_url)

    async def test_group_pagination(self):
        """Test that pagination works when getting the branches of a group of projects."""
        page1 = FakeResponse(self.branches[:3], links={"next": {"url": "https://gitlab/next_page"}})
        page2 = FakeResponse(self.branches[3:])
        responses = [self.group_exists(), self.group_projects(), page1, page2, self.group_exists()]
        measurement = await self.collect(get_request_side_effect=responses)
        self.assert_measurement(measurement, value="2", entities=self.entities, landing_url=self.group_landing_url)

    async def test_groups_endpoint_failure(self):
        """Test that a groups endpoint failure results in a failed measurement."""
        measurement = await self.collect(get_request_side_effect=[self.response_error(HTTPStatus.FORBIDDEN)])
        self.assert_measurement(measurement, connection_error="403", landing_url="https://gitlab")
