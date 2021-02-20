"""Azure Devops Server user story points collector."""

from source_model import SourceMeasurement, SourceResponses

from .issues import AzureDevopsIssues


class AzureDevopsUserStoryPoints(AzureDevopsIssues):
    """Collector to get user story points from Azure Devops Server."""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the story points from the work items."""
        measurement = await super()._parse_source_responses(responses)
        value = 0
        for entity, work_item in zip(measurement.entities, await self._work_items(responses)):
            entity["story_points"] = story_points = work_item["fields"].get("Microsoft.VSTS.Scheduling.StoryPoints")
            value += 0 if story_points is None else story_points
        measurement.value = str(round(value))
        return measurement
