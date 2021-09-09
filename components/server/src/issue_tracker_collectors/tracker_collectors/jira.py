"""Jira issues collector."""

from issue_tracker_collectors.base_tracker_collector import BaseTrackerCollector
from model.tracker_issue_status import TrackerIssueStatus
from server_utilities.type import URL


class Jira(BaseTrackerCollector):
    """Jira collector for issues."""

    def _api_url(self) -> URL:
        """Extend to get the fields from Jira and create a field name to field id mapping."""
        url = super()._api_url()
        return URL(f"{url}/rest/api/2/issue/{self._safe_tracker_issue}?fields=status")

    def _landing_url(self) -> URL:
        """Extend to add the JQL query to the landing URL."""
        url = super()._api_url()
        return URL(f"{url}/browse/{self._safe_tracker_issue}")

    def _parse_source_response(self, response) -> TrackerIssueStatus:
        """Override to get the issues from the responses."""
        json = response.json()
        name = json["fields"]["status"]["name"]
        description = json["fields"]["status"]["description"]
        status = TrackerIssueStatus(name, description=description)
        return status
