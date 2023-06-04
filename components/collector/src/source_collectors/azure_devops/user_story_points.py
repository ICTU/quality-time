"""Azure DevOps Server user story points collector."""

from typing import Final

from collector_utilities.functions import decimal_round_half_up
from collector_utilities.type import Value
from model import Entity, SourceResponses

from .issues import AzureDevopsIssues


class AzureDevopsUserStoryPoints(AzureDevopsIssues):
    """Collector to get user story points from Azure Devops Server."""

    _STORY_POINTS_FIELD: Final[str] = "Microsoft.VSTS.Scheduling.StoryPoints"
    _EFFORT_FIELD: Final[str] = "Microsoft.VSTS.Scheduling.Effort"

    def _item_select_fields(self) -> list[str]:
        """Also request all work item fields which may hold story point values."""
        base_fields = super()._item_select_fields()
        return [*base_fields, self._STORY_POINTS_FIELD, self._EFFORT_FIELD]

    def _parse_entity(self, work_item: dict) -> Entity:
        """Add the story points to the work item entity."""
        parsed_entity = super()._parse_entity(work_item)
        parsed_entity["story_points"] = self.__story_points(work_item)
        return parsed_entity

    async def _parse_value(self, responses: SourceResponses) -> Value:
        """Override to parse the sum of the user story points from the responses."""
        calculated_value = sum(self.__story_points(work_item) for work_item in await self._work_items(responses))
        return str(decimal_round_half_up(calculated_value))

    def __story_points(self, work_item: dict[str, dict[str, None | float]]) -> float:
        """Return the number of story points from the work item."""
        story_points = work_item["fields"].get(self._STORY_POINTS_FIELD)
        effort = work_item["fields"].get(self._EFFORT_FIELD)
        return story_points or effort or 0.0
