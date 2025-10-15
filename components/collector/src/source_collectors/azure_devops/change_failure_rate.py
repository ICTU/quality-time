"""Azure DevOps Server change failure rate collector."""

from itertools import pairwise
from typing import TYPE_CHECKING, cast

from collector_utilities.date_time import MAX_DATETIME, days_ago, parse_datetime
from model import Entities, Entity, SourceResponses

from .base import AzureDevopsPipelines
from .issues import AzureDevopsIssues

if TYPE_CHECKING:
    from datetime import datetime

    from collector_utilities.type import URL, Value


class AzureDevopsChangeFailureRate(AzureDevopsIssues, AzureDevopsPipelines):
    """Azure DevOps Server change failure rate collector."""

    def _item_select_fields(self) -> list[str]:
        """Extend to also request created date field to calculate issue age."""
        return [*super()._item_select_fields(), "System.CreatedDate"]

    async def _get_source_responses(self, *urls: URL) -> SourceResponses:
        """Override to first get the AzureDevopsPipelines responses, then extend with AzureDevopsIssues."""
        pipeline_ids = await self._active_pipelines()
        api_pipelines_urls = [await self._api_pipelines_url(pipeline_id) for pipeline_id in pipeline_ids]
        responses = await AzureDevopsPipelines._get_source_responses(self, *api_pipelines_urls)  # noqa: SLF001
        responses.extend(await AzureDevopsIssues._get_source_responses(self, *urls))  # noqa: SLF001
        return responses

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        issues = Entities()
        deployments = Entities()
        for response in responses:
            if response.url.name == "wiql":  # lookup for AzureDevopsIssues ids, no entities
                continue
            if response.url.name == "workitemsbatch":  # issues from AzureDevopsIssues
                issue_responses = SourceResponses(responses=[response, response], api_url=response.url)
                # first response is ignored by AzureDevopsIssues._parse_entities, as it is for the workItems (wiql) api
                parsed_issues = await AzureDevopsIssues._parse_entities(self, issue_responses)  # noqa: SLF001
                issues.extend([issue for issue in parsed_issues if self._include_issue(issue)])
            else:  # deployments from AzureDevopsPipelines
                deployments.extend(await self._parse_pipeline_entities(response))
        if deployments:
            deployments.sort(key=lambda d: parse_datetime(d["build_date"]))  # oldest to newest
            for this_dep, next_dep in pairwise(deployments):  # only iterate if there are at least two deployments
                this_dep["failed"] = self.issues_in_interval(
                    issues,
                    self.deployment_timestamp(this_dep),
                    self.deployment_timestamp(next_dep),
                )
            latest_dep = deployments[-1]  # latest deployment was not iterated by pairwise; do it separately
            latest_dep["failed"] = self.issues_in_interval(issues, self.deployment_timestamp(latest_dep), MAX_DATETIME)
        return deployments

    @staticmethod
    def issue_timestamp(issue: Entity) -> datetime:
        """Return the datetime of issue entities."""
        return parse_datetime(issue["created"])

    @staticmethod
    def deployment_timestamp(entity: Entity) -> datetime:
        """Return the datetime of deployment entities."""
        return parse_datetime(entity["build_date"])

    def issues_in_interval(self, issues, dt_start, dt_end) -> bool:
        """Return whether there are issues contained within the given interval (dt_start, dt_end]."""
        return any(issue for issue in issues if dt_start < self.issue_timestamp(issue) <= dt_end)

    def _parse_entity(self, work_item: dict) -> Entity:
        """Add the created date to the issue entity."""
        parsed_entity = AzureDevopsIssues._parse_entity(self, work_item)  # noqa: SLF001
        parsed_entity["created"] = work_item["fields"]["System.CreatedDate"]
        return parsed_entity

    def _include_issue(self, issue: Entity) -> bool:
        """Return whether this issue should be included."""
        created_age = days_ago(parse_datetime(issue["created"]))
        max_created_age = int(cast(str, self._parameter("lookback_days_issues")))
        return created_age <= max_created_age

    def _include_entity(self, entity: Entity) -> bool:
        """Return whether this pipeline should be counted."""
        build_age = days_ago(self.deployment_timestamp(entity))
        max_age = int(cast(str, self._parameter("lookback_days_pipeline_runs")))
        return entity["failed"] and build_age <= max_age

    async def _parse_value(self, responses: SourceResponses, included_entities: Entities) -> Value:
        """Calculate the numerator of the change failure rate."""
        return str(len(included_entities))
