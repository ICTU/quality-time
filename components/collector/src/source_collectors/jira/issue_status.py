"""Jira issue status collector."""

from base_collectors import SourceCollector
from collector_utilities.type import URL
from model import IssueStatus, SourceMeasurement, SourceResponses


class JiraIssueStatus(SourceCollector):
    """Jira issue status collector."""

    async def _api_url(self) -> URL:
        """Extend to get the fields from Jira and create a field name to field id mapping."""
        url = await super()._api_url()
        return URL(f"{url}/rest/api/2/issue/{self._issue}?fields=status")

    async def _landing_url(self) -> URL:
        """Extend to add the JQL query to the landing URL."""
        url = await super()._api_url()
        return URL(f"{url}/browse/{self._issue}")

    async def _parse_issue_status(self, responses: SourceResponses) -> IssueStatus:
        """Override to get the issues from the responses."""
        json = await responses[0].json()
        name = json["fields"]["status"]["name"]
        description = json["fields"]["status"]["description"]
        return IssueStatus(self._issue, name=name, description=description)
