"""Change failure rate collector."""

from datetime import datetime
from itertools import pairwise
from typing import TYPE_CHECKING, ClassVar, cast

from base_collectors import MetricCollector
from collector_utilities.date_time import MAX_DATETIME, parse_datetime
from model import Entities, Entity, MetricMeasurement, SourceMeasurement

if TYPE_CHECKING:
    from collections.abc import Sequence


class ChangeFailureRate(MetricCollector):
    """Change failure rate collector."""

    # Partial sources for issues and deployments, which need to be combined within this metric
    ISSUE_SOURCE_TYPES: ClassVar[list[str]] = ["jira"]
    DEPLOYMENT_SOURCE_TYPES: ClassVar[list[str]] = ["gitlab", "jenkins"]

    async def collect(self) -> MetricMeasurement | None:
        """Override to calculate the composite value."""
        if (measurement := await super().collect()) is None:
            return None
        # No need to keep track of deployments in Azure DevOps here, this is handled by its source collector
        issues = self.issue_entities(measurement.sources)
        deployments = self.deployment_entities(measurement.sources)
        if deployments:
            deployments.sort(key=self.deployment_timestamp)  # oldest to newest
            for this_dep, next_dep in pairwise(deployments):  # only iterate if there are at least two deployments
                this_dep["failed"] = self.issues_in_interval(
                    issues,
                    self.deployment_timestamp(this_dep),
                    self.deployment_timestamp(next_dep),
                )
            latest_dep = deployments[-1]  # latest deployment was not iterated by pairwise; do it separately
            latest_dep["failed"] = self.issues_in_interval(issues, self.deployment_timestamp(latest_dep), MAX_DATETIME)
        for source in measurement.sources:
            if self.source_type(source) in self.ISSUE_SOURCE_TYPES:
                # Set the values to zero as this metric only counts failed deployments
                source.total = source.value = "0"
            if self.source_type(source) in self.DEPLOYMENT_SOURCE_TYPES:
                source.total = str(len(source.get_entities()))
                # Only select failed deployments
                source.entities = Entities(
                    entity for entity in source.get_entities() if self._include_entity(entity, deployments)
                )
                source.value = str(len(source.entities))
        return measurement

    def source_type(self, source: SourceMeasurement) -> str:
        """Return the source type."""
        return str(self._metric["sources"][source.source_uuid]["type"])

    def issues_in_interval(self, issues, dt_start, dt_end) -> bool:
        """Return whether there are issues contained within the given interval (dt_start, dt_end]."""
        return any(issue for issue in issues if dt_start < self.issue_timestamp(issue) <= dt_end)

    def issue_sources(self, sources: Sequence[SourceMeasurement]) -> list[SourceMeasurement]:
        """Return the sources of failed deployments."""
        return [source for source in sources if self.source_type(source) in self.ISSUE_SOURCE_TYPES]

    def issue_entities(self, sources: Sequence[SourceMeasurement]) -> Entities:
        """Return the entities from sources of failed deployments."""
        return Entities(entity for source in self.issue_sources(sources) for entity in source.get_entities())

    def deployment_sources(self, sources: Sequence[SourceMeasurement]) -> list[SourceMeasurement]:
        """Return the sources of total deployments."""
        return [source for source in sources if self.source_type(source) in self.DEPLOYMENT_SOURCE_TYPES]

    def deployment_entities(self, sources: Sequence[SourceMeasurement]) -> Entities:
        """Return the entities from sources of total deployments."""
        return Entities(entity for source in self.deployment_sources(sources) for entity in source.get_entities())

    @staticmethod
    def issue_timestamp(issue: Entity) -> datetime:
        """Return the datetime of issue entities."""
        return parse_datetime(issue["created"])  # Jira only

    @staticmethod
    def deployment_timestamp(entity: Entity) -> datetime:
        """Return the datetime of deployment entities."""
        return cast(datetime, entity["build_datetime"])  # same for both GitLab and Jenkins

    def _include_entity(self, entity: Entity, deployments: Entities) -> bool:
        """Include the entity if it was marked as a failed."""
        return any(deployment.get("failed") for deployment in deployments if deployment["key"] == entity["key"])
