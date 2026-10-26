"""Jira change failure rate issue collector."""

from typing import cast

from shared.utils.date_time import parse_datetime

from collector_utilities.date_time import days_ago

from .issues import JiraIssues


class JiraChangeFailureRate(JiraIssues):
    """Collector to get change failure rate from Jira."""

    def _include_issue(self, issue: dict) -> bool:
        """Return whether this issue should be included."""
        return days_ago(parse_datetime(issue["fields"]["created"])) <= int(cast(str, self._parameter("lookback_days")))
