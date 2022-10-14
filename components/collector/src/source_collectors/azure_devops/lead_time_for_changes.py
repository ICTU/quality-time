"""Azure DevOps Server lead time for changes collector."""

from statistics import mean
from typing import cast

from dateutil.parser import parse

from collector_utilities.functions import days_ago
from collector_utilities.type import Value
from model import Entity, Entities, SourceResponses

from .issues import AzureDevopsIssues


class AzureDevopsLeadTimeForChanges(AzureDevopsIssues):
    """Collector to calculate lead time for changes from Azure Devops Server."""

    def _item_select_fields(self) -> list[str]:
        """Also request date fields to calculate lead time."""
        base_fields = super()._item_select_fields()
        return base_fields + ["System.CreatedDate", "System.ChangedDate"]

    def _include_issue(self, issue: dict) -> bool:
        """Return whether this issue should be counted."""
        if not issue["fields"]["System.State"] in ["Closed", "Done"]:
            return False

        finished_date = issue["fields"].get("System.ChangedDate")  # TODO - how to find out System.State update ?
        if not finished_date:
            return False

        return days_ago(parse(finished_date)) <= int(cast(str, self._parameter("lookback_days")))

    async def _parse_value(self, responses: SourceResponses) -> Value:
        work_items = (await self._work_items(responses))
        if not work_items:
            return None

        lead_times = [self.__lead_time(item) for item in work_items]
        return str(round(mean(lead_times)))

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Override to add the story points to the entities."""
        return Entities(
            Entity(
                key=work_item["id"],
                project=work_item["fields"]["System.TeamProject"],
                title=work_item["fields"]["System.Title"],
                work_item_type=work_item["fields"]["System.WorkItemType"],
                state=work_item["fields"]["System.State"],
                url=work_item["url"],
                lead_time=self.__lead_time(work_item),
            )
            for work_item in await self._work_items(responses)
        )

    @staticmethod
    def __lead_time(work_item: dict[str, dict[str, str]]) -> int:
        """Return the lead time of a completed work item."""
        changed_date = parse(work_item["fields"]["System.ChangedDate"])
        created_date = parse(work_item["fields"]["System.CreatedDate"])
        return (changed_date - created_date).days
