"""Jira average issue lead time collector."""

from statistics import mean
from typing import TYPE_CHECKING, cast

from collector_utilities.date_time import days_ago, parse_datetime

from .issues import JiraIssues

if TYPE_CHECKING:
    from collector_utilities.type import URL, Value
    from model import Entities, Entity


class JiraAverageIssueLeadTime(JiraIssues):
    """Jira collector for average issue lead time."""

    def _include_issue(self, issue: dict) -> bool:
        """Return whether this issue should be counted."""
        if issue["fields"]["status"]["statusCategory"]["key"] != "done":
            return False
        if not (finished_date := issue["fields"].get("updated")):
            return False
        return days_ago(parse_datetime(finished_date)) <= int(cast(str, self._parameter("lookback_days")))

    def _create_entity(self, issue: dict, url: URL) -> Entity:
        """Extend to also add the lead time to the entity."""
        entity = super()._create_entity(issue, url)
        entity["lead_time"] = str(self.__lead_time(issue["fields"]))
        return entity

    @classmethod
    def _compute_value(cls, entities: Entities) -> Value:
        """Calculate the average lead time of the completed issues."""
        lead_times = [cls.__lead_time(issue) for issue in entities]
        return str(round(mean(lead_times))) if entities else None

    @staticmethod
    def __lead_time(issue: dict) -> int:
        """Return the lead time of the completed issue."""
        return (parse_datetime(issue["updated"]) - parse_datetime(issue["created"])).days
