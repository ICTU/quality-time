"""Jira issue status collector."""

from typing import cast

from collector_utilities.type import URL
from model import Issue, IssueSprint, IssueStatus, IssueStatusCategory, SourceResponses

from .base import JiraBase


class JiraIssueStatus(JiraBase):
    """Jira issue status collector."""

    # Map the Jira status categories, the keys, to the Quality-time status categories, the values:
    STATUS_CATEGORY_MAPPING = dict(done="done", indeterminate="doing", new="todo")

    # Note, Jira distinguishes statuses and status categories. Statuses can be added, but the list of status
    # categories is fixed, per https://jira.atlassian.com/browse/JRASERVER-36241. As Quality-time only needs to know
    # whether a issue is done or not, we use status categories to keep track of that and to color the issues in the
    # UI. We do add the status name to the issue and display it in the UI, but the status is not interpreted.

    async def _api_url(self) -> URL:
        """Override to get the issue, including the status field, from Jira."""
        url = await super()._api_url()
        return URL(f"{url}/rest/agile/1.0/issue/{self._issue_id}?fields=created,status,summary,updated,duedate,sprint")

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
        duedate = json["fields"].get("duedate")
        summary = json["fields"].get("summary")
        jira_sprint = json["fields"].get("sprint", {})
        sprint = IssueSprint(jira_sprint.get("name"), jira_sprint.get("state"), jira_sprint.get("endDate"))
        issue = Issue(name, summary, created, updated, duedate, sprint)
        return IssueStatus(self._issue_id, issue=issue, status_category=status_category)
