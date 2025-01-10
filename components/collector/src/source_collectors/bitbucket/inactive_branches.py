"""Bitbucket inactive branches collector."""

from datetime import datetime
from typing import cast

from base_collectors import BranchType, InactiveBranchesSourceCollector
from collector_utilities.exceptions import NotFoundError
from collector_utilities.type import URL
from dateutil.tz import tzutc
from model import SourceResponses

from .base import BitbucketProjectBase


class BitbucketBranchInfoError(NotFoundError):
    """Bitbucket branch info is missing."""

    def __init__(self, project: str) -> None:
        tip = (
            "Please check if the repository (name with owner) and access token (with repo scope) are "
            "configured correctly."
        )
        super().__init__("Branch info for repository", project, extra=tip)

class BitbucketBranchType(BranchType):
    """Bitbucket branch information as returned by the API."""

    default: bool
    last_commit: datetime


class BitbucketInactiveBranches[Branch: BitbucketBranchType](BitbucketProjectBase, InactiveBranchesSourceCollector):
    """Collector for inactive branches."""

    async def _api_url(self) -> URL:
        """Override to return the branches API."""
        return await self._bitbucket_api_url("branches")

    async def _landing_url(self, responses: SourceResponses) -> URL:
        """Extend to add the project branches."""
        return URL(f"{await super()._landing_url(responses)}/{self._parameter('project')}/browse")

    async def _branches(self, responses: SourceResponses) -> list[Branch]:
        """Return a list of branches from the responses."""
        branches = []
        for response in responses:
            json = await response.json()
            metadata = "com.atlassian.bitbucket.server.bitbucket-branch:latest-commit-metadata"
            branches.extend([
                BitbucketBranchType(
                    name=branch["displayId"],
                    default=branch["isDefault"],
                    last_commit=datetime.fromtimestamp(branch["metadata"][metadata]["committerTimestamp"] / 1e3,
                        tz=tzutc()),
                    id=branch["id"]
                )
                for branch in json["values"]
            ])
        if len(branches) == 0:
            project = f"projects/{self._parameter('owner')}/repos/{self._parameter('repository')}"
            raise BitbucketBranchInfoError(project)
        return branches

    def _is_default_branch(self, branch: Branch) -> bool:
        """Return whether the branch is the default branch."""
        return branch["default"]

    def _is_branch_merged(self, branch: Branch) -> bool:
        """Return whether the branch has been merged with the default branch."""
        return False

    def _commit_datetime(self, branch: Branch) -> datetime:
        """Override to parse the commit date from the branch."""
        return branch["last_commit"]

    def _branch_landing_url(self, branch: Branch) -> URL:
        """Override to get the landing URL from the branch."""
        instance_url=super()._parameter("url")
        project = f"projects/{self._parameter('owner')}/repos/{self._parameter('repository')}/browse?at="
        branch_id = branch.get("id").lstrip("/")
        return cast(URL, f"{instance_url}/{project}{branch_id or ""}")
