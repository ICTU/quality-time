"""Jira issue status collector."""

from base_collectors import SourceCollector
from collector_utilities.type import URL
from model import IssueStatus, SourceResponses


class JiraIssueStatus(SourceCollector):
    """Jira issue status collector."""

    async def _api_url(self) -> URL:
        """Override to get the issue, including the status field, from Jira."""
        url = self._source.get("url", "").strip("/")
        return URL(f"{url}/rest/api/2/issue/{self._issue}?fields=status")

    async def _landing_url(self, responses: SourceResponses) -> URL:
        """Override to add the issue to the landing URL."""
        url = self._source.get("url", "").strip("/")
        return URL(f"{url}/browse/{self._issue}")

    async def _parse_issue_status(self, responses: SourceResponses) -> IssueStatus:
        """Override to get the issue status from the responses."""
        json = await responses[0].json()
        name = json["fields"]["status"]["name"]
        description = json["fields"]["status"]["description"]
        return IssueStatus(self._issue, name=name, description=description)
