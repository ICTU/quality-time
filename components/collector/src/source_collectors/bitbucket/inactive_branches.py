"""Bitbucket inactive branches collector."""

from datetime import datetime
from typing import cast

from base_collectors import BranchType, InactiveBranchesSourceCollector
from collector_utilities.date_time import parse_datetime
from collector_utilities.type import URL
from model import SourceResponses

from .base import BitbucketProjectBase


class BitbucketBranchType(BranchType):
    """Bitbucket branch information as returned by the API."""

    commit: dict[str, str]
    default: bool
    merged: bool
    web_url: str


class BitbucketInactiveBranches[Branch: BitbucketBranchType](BitbucketProjectBase, InactiveBranchesSourceCollector):
    """Collector for inactive branches."""

    async def _api_url(self) -> URL:
        """Override to return the branches API."""
        return await self._bitbucket_api_url("repository/branches")

    async def _landing_url(self, responses: SourceResponses) -> URL:
        """Extend to add the project branches."""
        return URL(f"{await super()._landing_url(responses)}/{self._parameter('project')}/-/branches")

    async def _branches(self, responses: SourceResponses) -> list[Branch]:
        """Return a list of branches from the responses."""
        branches = []
        for response in responses:
            branches.extend(await response.json())
        return branches

    def _is_default_branch(self, branch: Branch) -> bool:
        """Return whether the branch is the default branch."""
        return branch["default"]

    def _is_branch_merged(self, branch: Branch) -> bool:
        """Return whether the branch has been merged with the default branch."""
        return branch["merged"]

    def _commit_datetime(self, branch: Branch) -> datetime:
        """Override to parse the commit date from the branch."""
        return parse_datetime(branch["commit"]["committed_date"])

    def _branch_landing_url(self, branch: Branch) -> URL:
        """Override to get the landing URL from the branch."""
        return cast(URL, branch.get("web_url") or "")
