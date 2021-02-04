"""Unit tests for the Azure Devops Server unmerged branches collector."""

from .base import AzureDevopsTestCase


class AzureDevopsUnmergedBranchesTest(AzureDevopsTestCase):
    """Unit tests for the Azure DevOps Server unmerged branches."""

    def setUp(self):
        """Extend to set up the metric under test."""
        super().setUp()
        self.sources["source_id"]["parameters"]["branches_to_ignore"] = ["ignored_.*"]
        self.metric = dict(type="unmerged_branches", sources=self.sources, addition="sum")
        self.repositories = dict(value=[dict(id="id", name="project")])
        self.landing_url = f"{self.url}/_git/project/branches"

    async def test_no_branches_except_master(self):
        """Test that the number of unmerged branches is returned."""
        branches = dict(value=[dict(name="master", isBaseVersion=True)])
        response = await self.collect(self.metric, get_request_json_side_effect=[self.repositories, branches])
        self.assert_measurement(response, value="0", entities=[], landing_url=self.landing_url)

    async def test_unmerged_branches(self):
        """Test that the number of unmerged branches is returned."""
        timestamp = "2019-09-03T20:43:00Z"
        branches = dict(
            value=[
                dict(name="master", isBaseVersion=True),
                dict(
                    name="branch",
                    isBaseVersion=False,
                    aheadCount=1,
                    commit=dict(committer=dict(date=timestamp), url="https://commit"),
                ),
                dict(
                    name="ignored_branch",
                    isBaseVersion=False,
                    aheadCount=1,
                    commit=dict(committer=dict(date=timestamp)),
                ),
            ]
        )
        response = await self.collect(self.metric, get_request_json_side_effect=[self.repositories, branches])
        self.assert_measurement(
            response,
            value="1",
            landing_url=self.landing_url,
            entities=[dict(name="branch", key="branch", commit_date="2019-09-03", url="https://commit")],
        )
