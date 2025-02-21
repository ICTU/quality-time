"""Unit tests for the Bitbucket inactive branches collector."""

from datetime import datetime

from dateutil.tz import tzutc

from .base import BitbucketBranchesTestCase


class BitbucketInactiveBranchesTest(BitbucketBranchesTestCase):
    """Unit tests for the inactive branches metric."""

    METRIC_TYPE = "inactive_branches"

    def setUp(self):
        """Extend to setup fixtures."""
        super().setUp()
        self.landing_url = "https://bitbucket/projects/owner/repos/repository/browse"
        self.set_source_parameter("branches_to_ignore", ["ignored_.*"])
        main = self.create_branch("main", default=True)
        unmerged = self.create_branch("unmerged_branch")
        ignored = self.create_branch("ignored_branch")
        active_unmerged = self.create_branch("active_unmerged_branch", active=True)
        self.branches = self.create_branches_json([main, unmerged, ignored, active_unmerged])
        self.unmerged_branch_entity = self.create_entity("unmerged_branch")
        self.entities = [self.unmerged_branch_entity]

    def create_branch(
        self, name: str, *, default: bool = False, active: bool = False
    ) -> dict[str, str | bool | dict[str, dict[str, float | int]]]:
        """Create a Bitbucket branch."""
        commit_date = (datetime.now(tz=tzutc()).timestamp() if active else 1554197584) * 1000
        return {
            "id": "refs/heads/" + name,
            "displayId": name,
            "type": "BRANCH",
            "latestCommit": "ef6a9d214d509461f62f5f79b6444db55aaecc78",
            "latestChangeset": "ef6a9d214d509461f62f5f79b6444db55aaecc78",
            "isDefault": default,
            "metadata": {
                "com.atlassian.bitbucket.server.bitbucket-branch:latest-commit-metadata": {
                    "committerTimestamp": commit_date
                }
            },
        }

    def create_branches_json(self, branches, has_next_page: bool = False):
        """Create an entity."""
        return {
            "size": len(branches),
            "limit": 25,
            "isLastPage": True,
            "start": 0,
            "hasNextPage": has_next_page,
            "values": branches,
        }

    def create_entity(self, name: str) -> dict[str, str]:
        """Create an entity."""
        return {
            "key": name,
            "name": name,
            "commit_date": "2019-04-02",
            "merge_status": "unmerged",
            "url": self.landing_url + "?at=refs/heads/" + name,
        }

    async def test_inactive_branches(self):
        """Test that the number of inactive branches can be measured."""
        response = await self.collect(get_request_json_return_value=self.branches)
        self.assert_measurement(response, value="1", entities=self.entities, landing_url=self.landing_url)

    async def test_unmerged_inactive_branches(self):
        """Test that the number of unmerged inactive branches can be measured."""
        self.set_source_parameter("branch_merge_status", ["unmerged"])
        response = await self.collect(get_request_json_return_value=self.branches)
        self.assert_measurement(
            response, value="1", entities=[self.unmerged_branch_entity], landing_url=self.landing_url
        )

    async def test_no_branches_found(self):
        """Test that a parse error is returned when no branches are found."""
        response = await self.collect(get_request_json_return_value={"isLastPage": True, "values": []})
        self.assert_measurement(response, landing_url=self.landing_url, parse_error="Branch info for repository")

    async def test_private_token(self):
        """Test that the private token is used."""
        self.set_source_parameter("private_token", "token")
        _, get, _ = await self.collect(get_request_json_return_value=self.branches, return_mocks=True)
        get.assert_called_once_with(
            "https://bitbucket/rest/api/1.0/projects/owner/repos/repository/branches?limit100&&details=true&start=0",
            allow_redirects=True,
            auth=None,
            headers={"Authorization": "Bearer token"},
        )
