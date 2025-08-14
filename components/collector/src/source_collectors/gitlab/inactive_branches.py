"""GitLab inactive branches collector."""

from datetime import datetime
from http import HTTPStatus
from typing import cast

import aiohttp

from base_collectors import BranchType, InactiveBranchesSourceCollector
from collector_utilities.date_time import parse_datetime
from collector_utilities.functions import add_query
from collector_utilities.type import URL
from model import SourceResponses

from .base import GitLabBase


class GitLabBranchType(BranchType):
    """GitLab branch information as returned by the API."""

    commit: dict[str, str]
    default: bool
    merged: bool
    web_url: str


class GitLabInactiveBranches[Branch: GitLabBranchType](GitLabBase, InactiveBranchesSourceCollector):
    """Collector for inactive branches."""

    async def _landing_url(self, responses: SourceResponses) -> URL:
        """Extend to add the project branches."""
        project_or_group = self._parameter("project_or_group")
        landing_path = project_or_group if await self._project_is_group() else f"{project_or_group}/-/branches"
        return URL(f"{await super()._landing_url(responses)}/{landing_path}")

    async def _get_source_responses(self, *urls: URL) -> SourceResponses:
        """Extend to get branches for a project or for multiple projects in a group."""
        project_or_group = cast(str, self._parameter("project_or_group", quote=True))
        if await self._project_is_group():
            group = project_or_group
            group_projects_url = add_query(
                URL(f"{await self._api_url()}/api/v4/groups/{group}/projects"), self.PAGE_SIZE, "include_subgroups=true"
            )
            projects = []
            for response in await super()._get_source_responses(group_projects_url):
                json = await response.json()
                projects.extend([project["path_with_namespace"] for project in json])
        else:
            projects = [project_or_group]
        repo_branches_urls = [
            add_query(URL(f"{await self._api_url()}/api/v4/projects/{project}/repository/branches"), self.PAGE_SIZE)
            for project in projects
        ]
        return await super()._get_source_responses(*repo_branches_urls)

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

    async def _project_is_group(self) -> bool:
        """Return whether the project parameter is actually a group of projects, as opposed to a single project."""
        project_or_group = self._parameter("project_or_group", quote=True)
        groups_url = URL(f"{await self._api_url()}/api/v4/groups/{project_or_group}")
        try:
            await super()._get_source_responses(groups_url)
        except aiohttp.ClientResponseError as message:
            if message.status == HTTPStatus.NOT_FOUND:
                return False
            raise
        return True
