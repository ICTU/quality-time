"""GitLab unmerged branches collector."""

from datetime import datetime
from typing import Any, Dict, List, cast

from dateutil.parser import parse

from base_collectors import UnmergedBranchesSourceCollector
from collector_utilities.functions import days_ago, match_string_or_regular_expression
from collector_utilities.type import URL
from source_model import SourceResponses

from .base import GitLabBase


class GitLabUnmergedBranches(GitLabBase, UnmergedBranchesSourceCollector):
    """Collector class to measure the number of unmerged branches."""

    async def _api_url(self) -> URL:
        """Override to return the branches API."""
        return await self._gitlab_api_url("repository/branches")

    async def _landing_url(self, responses: SourceResponses) -> URL:
        """Extend to add the project branches."""
        return URL(f"{str(await super()._landing_url(responses))}/{self._parameter('project')}/-/branches")

    async def _unmerged_branches(self, responses: SourceResponses) -> List[Dict[str, Any]]:
        """Override to return a list of unmerged and inactive branches."""
        branches = await responses[0].json()
        return [
            branch
            for branch in branches
            if not branch["default"]
            and not branch["merged"]
            and days_ago(self._commit_datetime(branch)) > int(cast(str, self._parameter("inactive_days")))
            and not match_string_or_regular_expression(branch["name"], self._parameter("branches_to_ignore"))
        ]

    def _commit_datetime(self, branch) -> datetime:
        """Override to parse the commit date from the branch."""
        return parse(branch["commit"]["committed_date"])

    def _branch_landing_url(self, branch) -> URL:
        """Override to get the landing URL from the branch."""
        return URL(branch.get("web_url", ""))
