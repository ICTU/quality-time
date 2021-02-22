"""Azure Devops Server unmerged branches collector."""

from datetime import datetime
from typing import Any, cast

from dateutil.parser import parse

from base_collectors import UnmergedBranchesSourceCollector
from collector_utilities.functions import days_ago, match_string_or_regular_expression
from collector_utilities.type import URL
from source_model import SourceResponses

from .base import AzureDevopsRepositoryBase


class AzureDevopsUnmergedBranches(UnmergedBranchesSourceCollector, AzureDevopsRepositoryBase):
    """Collector for unmerged branches."""

    async def _api_url(self) -> URL:
        """Extend to add the branches API path."""
        api_url = str(await super()._api_url())
        return URL(f"{api_url}/stats/branches?api-version=4.1")

    async def _landing_url(self, responses: SourceResponses) -> URL:
        """Extend to add the branches path."""
        landing_url = str(await super()._landing_url(responses))
        return URL(f"{landing_url}/branches")

    async def _unmerged_branches(self, responses: SourceResponses) -> list[dict[str, Any]]:
        """Override to get the unmerged branches response.

        Branches are considered unmerged if they have a base branch, have commits that are not on the base branch,
        have not been committed to for a minimum number of days, and are not to be ignored.
        """
        return [
            branch
            for branch in (await responses[0].json())["value"]
            if not branch["isBaseVersion"]
            and int(branch["aheadCount"]) > 0
            and days_ago(self._commit_datetime(branch)) > int(cast(str, self._parameter("inactive_days")))
            and not match_string_or_regular_expression(branch["name"], self._parameter("branches_to_ignore"))
        ]

    def _commit_datetime(self, branch) -> datetime:
        """Override to get the date and time of the most recent commit."""
        return parse(branch["commit"]["committer"]["date"])

    def _branch_landing_url(self, branch) -> URL:
        """Override to return the landing URL for the branch."""
        return URL(branch["commit"]["url"])
