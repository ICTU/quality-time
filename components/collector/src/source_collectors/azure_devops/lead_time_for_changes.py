"""Azure DevOps Server lead time for changes collector."""

from statistics import mean
from typing import cast

from dateutil.parser import parse

from collector_utilities.functions import days_ago
from collector_utilities.type import Value
from model import SourceResponses

from .issues import AzureDevopsIssues


class AzureDevopsLeadTimeForChanges(AzureDevopsIssues):
    """Collector to calculate lead time for changes from Azure Devops Server."""

    def _item_select_fields(self) -> list[str]:
        """Extend to also request date fields to calculate lead time."""
        return super()._item_select_fields() + ["System.CreatedDate", "System.ChangedDate"]

    def _include_issue(self, issue: dict) -> bool:
        """Return whether this issue should be counted."""
        if issue["fields"]["System.State"] not in ["Closed", "Done"]:
            return False
        if not (finished_date := issue["fields"].get("System.ChangedDate")):
            return False
        return days_ago(parse(finished_date)) <= int(cast(str, self._parameter("lookback_days")))

    async def _parse_value(self, responses: SourceResponses) -> Value:
        """Calculate the average lead time of the completed work items."""
        if work_items := (await self._work_items(responses)):
            lead_times = [self.__lead_time(item) for item in work_items]
            return str(round(mean(lead_times)))
        return None

    def _parse_entity(self, work_item: dict) -> dict:
        """Add the lead time to the work item entity"""
        parsed_entity = super()._parse_entity(work_item)
        parsed_entity['lead_time'] = self.__lead_time(work_item)
        return parsed_entity

    @staticmethod
    def __lead_time(work_item: dict[str, dict[str, str]]) -> int:
        """Return the lead time of a completed work item."""
        changed_date = parse(work_item["fields"]["System.ChangedDate"])
        created_date = parse(work_item["fields"]["System.CreatedDate"])
        return (changed_date - created_date).days
