"""SonarQube remediation effort collector."""

from typing import Dict, List

from collector_utilities.type import URL
from source_model import Entity, SourceResponses

from .base import SonarQubeMetricsBaseClass


class SonarQubeRemediationEffort(SonarQubeMetricsBaseClass):
    """SonarQube violation (technical debt) remediation effort."""

    def _landing_url_metric_key(self) -> str:
        """Override to return the metric key for the landing url."""
        # The landing url can point to one metric, so if the user selected one effort type point the landing url to
        # that metric. If not, the landing url points to the project overview.
        effort_types = self.__effort_types()
        return effort_types[0] if len(effort_types) == 1 else ""

    def _value_key(self) -> str:
        """Override to return the metric keys to use for the metric value."""
        return ",".join(self.__effort_types())

    async def _entities(self, metrics: Dict[str, str]) -> List[Entity]:
        """Override to return the effort entities."""
        entities = []
        api_values = self._data_model["sources"][self.source_type]["parameters"]["effort_types"]["api_values"]
        for effort_type in self.__effort_types():
            effort_type_description = [param for param, api_key in api_values.items() if effort_type == api_key][0]
            entities.append(
                Entity(
                    key=effort_type,
                    effort_type=effort_type_description,
                    effort=metrics[effort_type],
                    url=await self.__effort_type_landing_url(effort_type),
                )
            )
        return entities

    async def __effort_type_landing_url(self, effort_type: str) -> URL:
        """Generate a landing url for the effort type."""
        url = await super(SonarQubeMetricsBaseClass, self)._landing_url(  # pylint: disable=bad-super-call
            SourceResponses()
        )
        component = self._parameter("component")
        branch = self._parameter("branch")
        return URL(f"{url}/component_measures?id={component}&metric={effort_type}&branch={branch}")

    def __effort_types(self) -> List[str]:
        """Return the user-selected effort types."""
        return list(self._parameter("effort_types"))
