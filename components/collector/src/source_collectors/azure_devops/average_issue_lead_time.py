"""Azure DevOps Server average issue lead time collector."""

from statistics import mean
from typing import cast, Final

from dateutil.parser import parse

from collector_utilities.functions import days_ago
from collector_utilities.type import Value
from model import SourceResponses, Entity

from .issues import AzureDevopsIssues


class AzureDevopsAverageIssueLeadTime(AzureDevopsIssues):
    """Collector to calculate average issue lead time from Azure Devops Server."""

    _CREATED_DATE_FIELD: Final[str] = "System.CreatedDate"
    _CHANGED_DATE_FIELD: Final[str] = "System.ChangedDate"

    def _item_select_fields(self) -> list[str]:
        """Extend to also request date fields to calculate lead time."""
        return super()._item_select_fields() + [self._CREATED_DATE_FIELD, self._CHANGED_DATE_FIELD]

    def _include_entity(self, entity: Entity) -> bool:
        """Return whether this issue should be counted."""
        if entity["state"] not in ["Closed", "Done"]:
            return False
        if not entity["lead_time"]:  # no lead time means no changed date
            return False
        return days_ago(parse(entity["changed_field"])) <= int(cast(str, self._parameter("lookback_days")))

    async def _parse_value(self, responses: SourceResponses) -> Value:
        """Calculate the average lead time of the completed work items."""
        if work_items := await self._work_items(responses):
            lead_times = []
            for item in work_items:
                if lead_time := self.__lead_time(item):  # sadly, mypy does not understand short-circuiting this
                    lead_times.append(lead_time)
            if lead_times:
                return str(round(mean(lead_times)))
        return None

    def _parse_entity(self, work_item: dict) -> Entity:
        """Add the lead time to the work item entity"""
        parsed_entity = super()._parse_entity(work_item)
        issue_lead_time = self.__lead_time(work_item)
        parsed_entity["lead_time"] = issue_lead_time or ""
        parsed_entity["changed_field"] = work_item["fields"][self._CHANGED_DATE_FIELD] if issue_lead_time else ""
        return parsed_entity

    def __lead_time(self, work_item: dict[str, dict[str, str]]) -> int | None:
        """Return the lead time of a completed work item."""
        if not (changed_date_field := work_item["fields"].get(self._CHANGED_DATE_FIELD)):
            return None
        changed_date = parse(changed_date_field)
        created_date = parse(work_item["fields"][self._CREATED_DATE_FIELD])
        return (changed_date - created_date).days
