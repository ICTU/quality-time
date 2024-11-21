"""Unit tests for the Azure DevOps Server inactive branches collector."""

from .base import AzureDevopsTestCase


class AzureDevopsInactiveBranchesTest(AzureDevopsTestCase):
    """Unit tests for the Azure DevOps Server inactive branches."""

    METRIC_TYPE = "inactive_branches"

    def setUp(self):
        """Extend to set up the metric under test."""
        super().setUp()
        self.set_source_parameter("branches_to_ignore", ["ignored_.*"])
        self.repositories = {"value": [{"id": "id", "name": "project"}]}
        self.landing_url = f"{self.url}/_git/project/branches"
        self.timestamp = "2019-09-03T20:43:00Z"
        self.default_branch = self.create_branch("main", default=True)
        ignored_branch = self.create_branch("ignored_branch", ahead_count=1)
        unmerged_branch = self.create_branch("unmerged_branch", ahead_count=1)
        merged_branch = self.create_branch("merged_branch")
        self.branches = [self.default_branch, ignored_branch, merged_branch, unmerged_branch]
        self.merged_branch_entity = self.create_entity("merged_branch", merged=True)
        self.unmerged_branch_entity = self.create_entity("unmerged_branch", merged=False)

    def create_branch(
        self, name: str, *, ahead_count: int = 0, default: bool = False
    ) -> dict[str, str | bool | dict | int]:
        """Create an Azure DevOps branch."""
        return {
            "name": name,
            "isBaseVersion": default,
            "aheadCount": ahead_count,
            "commit": {"committer": {"date": self.timestamp}, "url": "https://commit"},
        }

    def create_entity(self, name: str, *, merged: bool) -> dict[str, str]:
        """Create an entity."""
        return {
            "name": name,
            "key": name,
            "commit_date": "2019-09-03",
            "merge_status": "merged" if merged else "unmerged",
            "url": "https://commit",
        }

    async def test_no_branches_except_default_branch(self):
        """Test that the number of inactive branches is returned."""
        branches = {"value": [self.default_branch]}
        response = await self.collect(get_request_json_side_effect=[self.repositories, branches])
        self.assert_measurement(response, value="0", entities=[], landing_url=self.landing_url)

    async def test_inactive_branches(self):
        """Test that the number of inactive branches is returned."""
        response = await self.collect(get_request_json_side_effect=[self.repositories, {"value": self.branches}])
        self.assert_measurement(
            response,
            value="2",
            landing_url=self.landing_url,
            entities=[self.merged_branch_entity, self.unmerged_branch_entity],
        )

    async def test_inactive_unmerged_branches(self):
        """Test that the number of inactive unmerged branches is returned."""
        self.set_source_parameter("branch_merge_status", ["unmerged"])
        response = await self.collect(get_request_json_side_effect=[self.repositories, {"value": self.branches}])
        self.assert_measurement(
            response,
            value="1",
            landing_url=self.landing_url,
            entities=[self.unmerged_branch_entity],
        )

    async def test_inactive_merged_branches(self):
        """Test that the number of inactive merged branches is returned."""
        self.set_source_parameter("branch_merge_status", ["merged"])
        response = await self.collect(get_request_json_side_effect=[self.repositories, {"value": self.branches}])
        self.assert_measurement(
            response,
            value="1",
            landing_url=self.landing_url,
            entities=[self.merged_branch_entity],
        )

    async def test_wrong_repository(self):
        """Test that if the repository cannot be found, an error message is returned."""
        self.set_source_parameter("repository", "wrong_repo")
        response = await self.collect(get_request_json_return_value=self.repositories)
        self.assert_measurement(
            response,
            landing_url=f"{self.url}/_git/wrong_repo/branches",
            connection_error="Repository 'wrong_repo' not found",
        )
