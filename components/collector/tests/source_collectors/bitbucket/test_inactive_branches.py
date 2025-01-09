"""Unit tests for the Bitbucket inactive branches collector."""

from datetime import datetime
from dateutil.tz import tzutc
from unittest.mock import AsyncMock

from .base import BitbucketTestCase


class BitbucketInactiveBranchesTest(BitbucketTestCase):
    """Unit tests for the inactive branches metric."""

    METRIC_TYPE = "inactive_branches"
    WEB_URL = "https://bitbucket/projects/owner/repos/repository/browse?at="

    def setUp(self):
        """Extend to setup fixtures."""
        super().setUp()
        self.set_source_parameter("branches_to_ignore", ["ignored_.*"])
        main = self.create_branch("main", default=True)
        unmerged = self.create_branch("unmerged_branch")
        ignored = self.create_branch("ignored_branch")
        active_unmerged = self.create_branch("active_unmerged_branch", active=True)
        self.branches = self.create_branches_json([main, unmerged, ignored, active_unmerged])
        self.unmerged_branch_entity = self.create_entity("unmerged_branch")
        self.entities = [self.unmerged_branch_entity]
        self.landing_url = "https://bitbucket/rest/api/1.0/projects/owner/repos/repository/branches?limit=100&details=true"

    def create_branch(
        self, name: str, *, default: bool = False, active: bool = False
    ) -> dict[str, str | bool | dict[str, str]]:
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
            }
        }

    def create_branches_json(self, branches):
        """Create an entity."""
        return {
            "size": len(branches),
            "limit": 25,
            "isLastPage": True,
            "start": 0,
            "values": branches
        }

    def create_entity(self, name: str) -> dict[str, str]:
        """Create an entity."""
        return {
            "key": name,
            "name": name,
            "commit_date": "2019-04-02",
            "merge_status": "unmerged",
            "url": self.WEB_URL + "refs/heads/" + name,
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

    async def test_private_token(self):
        """Test that the private token is used."""
        self.set_source_parameter("private_token", "token")
        inactive_branches_json = {"values": None}
        inactive_branches_response = AsyncMock()
        execute = AsyncMock(side_effect=[inactive_branches_response])
        inactive_branches_response.json = AsyncMock(return_value=inactive_branches_json)
        response = await self.collect(get_request_json_return_value=execute)
        self.assert_measurement(
            response,
            landing_url=self.landing_url,
            parse_error="Branch info for repository",
        )
