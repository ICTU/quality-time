"""Jira lead time for changes collector."""

from statistics import mean
from typing import cast

from dateutil.parser import parse

from collector_utilities.functions import days_ago
from collector_utilities.type import Value
from model import Entities

from .issues import JiraIssues


class JiraLeadTimeForChanges(JiraIssues):
    """Jira collector for lead time for changes."""

    def _include_issue(self, issue: dict) -> bool:
        if not super()._include_issue(issue):
            return False

        if not issue["fields"]["status"]["statusCategory"]["key"] == "done":
            return False

        finished_date = issue["fields"].get("updated")  # TODO - how to find out statusCategory update ?
        if not finished_date:
            return False

        return days_ago(parse(finished_date)) <= int(cast(str, self._parameter("lookback_days")))

    @classmethod
    def _compute_value(cls, entities: Entities) -> Value:
        if not entities:
            return None

        lead_times = []
        for issue in entities:
            issue_lead_time = parse(issue["updated"]) - parse(issue["created"])
            lead_times.append(issue_lead_time.days)

        return str(round(mean(lead_times)))
