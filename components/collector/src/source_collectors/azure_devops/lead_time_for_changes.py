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
        """Also request date fields to calculate lead time."""
        base_fields = super()._item_select_fields()
        return base_fields + ["System.CreatedDate", "System.ChangedDate"]

    def _include_issue(self, issue: dict) -> bool:
        """Return whether this issue should be counted."""
        if not issue["fields"]["System.State"] == "Closed":
            return False

        finished_date = issue["fields"].get("System.ChangedDate")  # TODO - how to find out System.State update ?
        if not finished_date:
            return False

        return days_ago(parse(finished_date)) <= int(cast(str, self._parameter("lookback_days")))

    async def _parse_value(self, responses: SourceResponses) -> Value:
        work_items = (await self._work_items(responses))
        if not work_items:
            return None

        lead_times = []
        for issue in work_items:
            issue_lead_time = parse(issue["System.ChangedDate"]) - parse(issue["System.CreatedDate"])
            lead_times.append(issue_lead_time.days)

        return str(round(mean(lead_times)))
