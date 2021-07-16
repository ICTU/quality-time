"""Azure Devops Server user story points collector."""

from typing import Optional

from collector_utilities.type import Value
from model import Entities, SourceResponses

from .issues import AzureDevopsIssues


class AzureDevopsUserStoryPoints(AzureDevopsIssues):
    """Collector to get user story points from Azure Devops Server."""

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Override to add the story points to the entities."""
        entities = await super()._parse_entities(responses)
        for entity, work_item in zip(entities, await self._work_items(responses)):
            entity["story_points"] = self.__story_points(work_item)
        return entities

    async def _parse_value(self, responses: SourceResponses) -> Value:
        """Override to parse the sum of the user story points from the responses."""
        return str(sum([self.__story_points(work_item) for work_item in await self._work_items(responses)], 0.0))

    @staticmethod
    def __story_points(work_item: dict[str, dict[str, Optional[float]]]) -> float:
        """Return the number of story points from the work item."""
        return work_item["fields"].get("Microsoft.VSTS.Scheduling.StoryPoints") or 0.0
