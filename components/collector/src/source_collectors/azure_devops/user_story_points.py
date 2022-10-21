"""Azure DevOps Server user story points collector."""

from collector_utilities.functions import decimal_round_half_up
from collector_utilities.type import Value
from model import Entity, Entities, SourceResponses

from .issues import AzureDevopsIssues


class AzureDevopsUserStoryPoints(AzureDevopsIssues):
    """Collector to get user story points from Azure Devops Server."""

    def _item_select_fields(self) -> list[str]:
        """Also request all work item fields which may hold story point values."""
        base_fields = super()._item_select_fields()
        return base_fields + ["Microsoft.VSTS.Scheduling.StoryPoints", "Microsoft.VSTS.Scheduling.Effort"]

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Override to add the story points to the entities."""
        return Entities(
            Entity(
                key=work_item["id"],
                project=work_item["fields"]["System.TeamProject"],
                title=work_item["fields"]["System.Title"],
                work_item_type=work_item["fields"]["System.WorkItemType"],
                state=work_item["fields"]["System.State"],
                url=work_item["_links"]["html"]["href"],
                story_points=self.__story_points(work_item),
            )
            for work_item in await self._work_items(responses)
        )

    async def _parse_value(self, responses: SourceResponses) -> Value:
        """Override to parse the sum of the user story points from the responses."""
        calculated_value = sum(self.__story_points(work_item) for work_item in await self._work_items(responses))
        return str(decimal_round_half_up(calculated_value))

    @staticmethod
    def __story_points(work_item: dict[str, dict[str, None | float]]) -> float:
        """Return the number of story points from the work item."""
        story_points = work_item["fields"].get("Microsoft.VSTS.Scheduling.StoryPoints")
        effort = work_item["fields"].get("Microsoft.VSTS.Scheduling.Effort")
        return story_points or effort or 0.0
