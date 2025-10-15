"""Azure DevOps Server inactive branches collector."""

from typing import TYPE_CHECKING, TypedDict, cast

from base_collectors import BranchType, InactiveBranchesSourceCollector
from collector_utilities.date_time import parse_datetime
from collector_utilities.type import URL

from .base import AzureDevopsRepositoryBase

if TYPE_CHECKING:
    from datetime import datetime

    from model import SourceResponses


class Commit(TypedDict):
    """Commit information as returned by the AzureDevOps API."""

    committer: dict[str, str]
    url: str


class AzureDevOpsBranchType(BranchType):
    """Azure DevOps branch information as returned by the AzureDevOps API."""

    commit: Commit
    aheadCount: int  # noqa:  N815
    isBaseVersion: bool  # noqa:  N815


class AzureDevopsInactiveBranches[Branch: AzureDevOpsBranchType](
    InactiveBranchesSourceCollector, AzureDevopsRepositoryBase
):
    """Collector for inactive branches."""

    async def _api_url(self) -> URL:
        """Extend to add the branches API path."""
        api_url = str(await super()._api_url())
        return URL(f"{api_url}/stats/branches?api-version=4.1")

    async def _landing_url(self, responses: SourceResponses) -> URL:
        """Extend to add the branches path."""
        landing_url = str(await super()._landing_url(responses))
        return URL(f"{landing_url}/branches")

    async def _branches(self, responses: SourceResponses) -> list[Branch]:
        """Return a list of branches from the responses."""
        return cast(list, (await responses[0].json())["value"])

    def _is_default_branch(self, branch: Branch) -> bool:
        """Return whether the branch is the default branch."""
        return branch["isBaseVersion"]

    def _is_branch_merged(self, branch: Branch) -> bool:
        """Return whether the branch has been merged with the default branch."""
        return branch["aheadCount"] == 0

    def _commit_datetime(self, branch: Branch) -> datetime:
        """Override to get the date and time of the most recent commit."""
        return parse_datetime(branch["commit"]["committer"]["date"])

    def _branch_landing_url(self, branch: Branch) -> URL:
        """Override to return the landing URL for the branch."""
        return URL(branch["commit"]["url"])
