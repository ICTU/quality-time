"""Jira issue status collector."""

from typing import cast

from collector_utilities.type import URL
from model import IssueStatus, IssueStatusCategory, SourceResponses

from .base import JiraBase


class JiraIssueStatus(JiraBase):
    """Jira issue status collector."""

    STATUS_CATEGORY_MAPPING = dict(done="done", indeterminate="doing", new="todo")

    async def _api_url(self) -> URL:
        """Override to get the issue, including the status field, from Jira."""
        url = await super()._api_url()
        return URL(f"{url}/rest/api/2/issue/{self._issue_id}?fields=created,status,summary,updated")

    async def _landing_url(self, responses: SourceResponses) -> URL:
        """Override to add the issue to the landing URL."""
        url = await super()._api_url()
        return URL(f"{url}/browse/{self._issue_id}")

    async def _parse_issue_status(self, responses: SourceResponses) -> IssueStatus:
        """Override to get the issue status from the responses."""
        json = await responses[0].json()
        name = json["fields"]["status"]["name"]
        jira_status_category = json["fields"]["status"]["statusCategory"]["key"]
        status_category = cast(IssueStatusCategory, self.STATUS_CATEGORY_MAPPING.get(jira_status_category, "todo"))
        created = json["fields"]["created"]
        updated = json["fields"].get("updated")
        summary = json["fields"].get("summary")
        return IssueStatus(
            self._issue_id,
            name=name,
            status_category=status_category,
            created=created,
            updated=updated,
            summary=summary,
        )
