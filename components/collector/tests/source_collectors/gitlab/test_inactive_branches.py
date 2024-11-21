"""Unit tests for the GitLab inactive branches collector."""

from datetime import datetime

from dateutil.tz import tzutc

from .base import GitLabTestCase


class GitLabInactiveBranchesTest(GitLabTestCase):
    """Unit tests for the inactive branches metric."""

    METRIC_TYPE = "inactive_branches"
    WEB_URL = "https://gitlab/namespace/project/-/tree/branch"

    def setUp(self):
        """Extend to setup fixtures."""
        super().setUp()
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
        self.landing_url = "https://gitlab/namespace/project/-/branches"

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

    async def test_inactive_branches(self):
        """Test that the number of inactive branches can be measured."""
        response = await self.collect(get_request_json_return_value=self.branches)
        self.assert_measurement(response, value="2", entities=self.entities, landing_url=self.landing_url)

    async def test_unmerged_inactive_branches(self):
        """Test that the number of unmerged inactive branches can be measured."""
        self.set_source_parameter("branch_merge_status", ["unmerged"])
        response = await self.collect(get_request_json_return_value=self.branches)
        self.assert_measurement(
            response, value="1", entities=[self.unmerged_branch_entity], landing_url=self.landing_url
        )

    async def test_merged_inactive_branches(self):
        """Test that the number of merged inactive branches can be measured."""
        self.set_source_parameter("branch_merge_status", ["merged"])
        response = await self.collect(get_request_json_return_value=self.branches)
        self.assert_measurement(response, value="1", entities=[self.merged_branch_entity], landing_url=self.landing_url)

    async def test_pagination(self):
        """Test that pagination works."""
        branches = [self.branches[:3], self.branches[3:]]
        links = {"next": {"url": "https://gitlab/next_page"}}
        response = await self.collect(get_request_json_side_effect=branches, get_request_links=links)
        self.assert_measurement(response, value="2", entities=self.entities, landing_url=self.landing_url)
