"""Jira change failure rate issue collector."""

from typing import cast

from collector_utilities.date_time import days_ago, parse_datetime

from .issues import JiraIssues


class JiraChangeFailureRate(JiraIssues):
    """Collector to get change failure rate from Jira."""

    def _include_issue(self, issue: dict) -> bool:
        """Return whether this issue should be included."""
        return days_ago(parse_datetime(issue["fields"]["created"])) <= int(cast(str, self._parameter("lookback_days")))
