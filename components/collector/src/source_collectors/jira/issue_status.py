"""Jira issue status collector."""

from typing import ClassVar, cast

from collector_utilities.type import URL
from model import Issue, IssueRelease, IssueSprint, IssueStatus, IssueStatusCategory, SourceResponses

from .base import JiraBase


class JiraIssueStatus(JiraBase):
    """Jira issue status collector."""

    # Map the Jira status categories, the keys, to the Quality-time status categories, the values:
    STATUS_CATEGORY_MAPPING: ClassVar[dict[str, str]] = {"done": "done", "indeterminate": "doing", "new": "todo"}

    # Note, Jira distinguishes statuses and status categories. Statuses can be added, but the list of status
    # categories is fixed, per https://jira.atlassian.com/browse/JRASERVER-36241. As Quality-time only needs to know
    # whether a issue is done or not, we use status categories to keep track of that and to color the issues in the
    # UI. We do add the status name to the issue and display it in the UI, but the status is not interpreted.

    async def _api_url(self) -> URL:
        """Override to get the issue, including the status field, from Jira."""
        url = await super()._api_url()
        fields = "created,status,summary,updated,duedate,fixVersions,sprint"
        # Capitalize the issue id because for some reason the URL is case sensitive and Jira ids are always full caps
        return url / f"rest/agile/1.0/issue/{self._issue_id.upper()}?fields={fields}"

    async def _get_source_responses(self, *urls: URL) -> SourceResponses:
        """Extend to also get the story points field, if it exists, from Jira."""
        await self._get_fields()
        story_points_field = f",{field_id}" if (field_id := self.__story_points_field_id()) else ""
        return await super()._get_source_responses(URL(f"{urls[0]}{story_points_field}"))

    def __story_points_field_id(self) -> str | None:
        """Return the id of the story points field, if it exists."""
        # Unlike the Jira metric collectors, don't fail if the field doesn't exist, as the story points are optional:
        return self._field_ids.get(str(self._parameter("story_points_field")).lower())

    async def _landing_url(self, responses: SourceResponses) -> URL:
        """Override to add the issue to the landing URL."""
        url = await super()._api_url()
        return url / f"browse/{self._issue_id}"  # Don't need upper() here; the browse URL is not case sensitive

    async def _parse_issue_status(self, responses: SourceResponses) -> IssueStatus:
        """Override to get the issue status from the responses."""
        json = await responses[0].json()
        fields = json["fields"]
        name = fields["status"]["name"]
        jira_status_category = fields["status"]["statusCategory"]["key"]
        status_category = cast(IssueStatusCategory, self.STATUS_CATEGORY_MAPPING.get(jira_status_category, "todo"))
        created = fields["created"]
        updated = fields.get("updated")
        duedate = fields.get("duedate")
        summary = fields.get("summary")
        release = self.__parse_issue_release(fields)
        sprint = self.__parse_issue_sprint(fields)
        story_points = self.__parse_issue_story_points(fields)
        issue = Issue(name, summary, created, updated, duedate, release, sprint, story_points)
        return IssueStatus(self._issue_id, issue=issue, status_category=status_category)

    @staticmethod
    def __parse_issue_release(fields) -> IssueRelease:
        """Parse the release from the Jira issue fields."""
        fix_versions = fields.get("fixVersions", [])
        # Issues can have multiple fix versions, assume the last one is the latest one:
        fix_version = fix_versions[-1] if fix_versions else {}
        return IssueRelease(fix_version.get("name"), fix_version.get("released"), fix_version.get("releaseDate"))

    @staticmethod
    def __parse_issue_sprint(fields) -> IssueSprint:
        """Parse the sprint from the Jira issue fields."""
        jira_sprint = fields.get("sprint") or {}
        return IssueSprint(jira_sprint.get("name"), jira_sprint.get("state"), jira_sprint.get("endDate"))

    def __parse_issue_story_points(self, fields) -> float | None:
        """Parse the story points from the Jira issue fields."""
        story_points = fields.get(field_id) if (field_id := self.__story_points_field_id()) else None
        return None if story_points is None else float(story_points)
