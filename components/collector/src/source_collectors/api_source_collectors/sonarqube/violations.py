"""SonarQube violations collector."""

from typing import Dict, List

from collector_utilities.type import URL
from source_model import Entity, SourceMeasurement, SourceResponses

from .base import SonarQubeCollector


class SonarQubeViolations(SonarQubeCollector):
    """SonarQube violations metric. Also base class for metrics that measure specific rules."""

    rules_configuration = ""  # Subclass responsibility
    types_parameter = "types"

    async def _landing_url(self, responses: SourceResponses) -> URL:
        url = await super()._landing_url(responses)
        component = self._parameter("component")
        branch = self._parameter("branch")
        landing_url = f"{url}/project/issues?id={component}&resolved=false&branch={branch}"
        return URL(landing_url + self.__rules_url_parameter())

    async def _api_url(self) -> URL:
        url = await super()._api_url()
        component = self._parameter("component")
        branch = self._parameter("branch")
        # If there's more than 500 issues only the first 500 are returned. This is no problem since we limit
        # the number of "entities" sent to the server anyway (that limit is 100 currently).
        api = (
            f"{url}/api/issues/search?componentKeys={component}&resolved=false&ps=500&"
            f"severities={self._violation_severities()}&types={self._violation_types()}&branch={branch}"
        )
        return URL(api + self.__rules_url_parameter())

    def __rules_url_parameter(self) -> str:
        """Return the rules url parameter, if any."""
        rules = (
            self._data_model["sources"][self.source_type]["configuration"][self.rules_configuration]["value"]
            if self.rules_configuration
            else []
        )
        return f"&rules={','.join(rules)}" if rules else ""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        value = 0
        entities: List[Entity] = []
        for response in responses:
            json = await response.json()
            value += int(json.get("total", 0))
            entities.extend([await self._entity(issue) for issue in json.get("issues", [])])
        return SourceMeasurement(value=str(value), entities=entities)

    async def __issue_landing_url(self, issue_key: str) -> URL:
        """Generate a landing url for the issue."""
        url = await super()._landing_url(SourceResponses())
        component = self._parameter("component")
        branch = self._parameter("branch")
        return URL(f"{url}/project/issues?id={component}&issues={issue_key}&open={issue_key}&branch={branch}")

    async def _entity(self, issue) -> Entity:
        """Create an entity from an issue."""
        return Entity(
            key=issue["key"],
            url=await self.__issue_landing_url(issue["key"]),
            message=issue["message"],
            severity=issue.get("severity", "no severity").lower(),
            type=issue["type"].lower(),
            component=issue["component"],
            creation_date=issue["creationDate"],
            update_date=issue["updateDate"],
        )

    def _violation_types(self) -> str:
        """Return the violation types."""
        return ",".join(violation_type.upper() for violation_type in list(self._parameter(self.types_parameter)))

    def _violation_severities(self) -> str:
        """Return the severities parameter."""
        return ",".join(severity.upper() for severity in self._parameter("severities"))


class SonarQubeViolationsWithPercentageScale(SonarQubeViolations):
    """SonarQube violations collectors that support the percentage scale."""

    total_metric = ""  # Subclass responsibility

    async def _get_source_responses(self, *urls: URL) -> SourceResponses:
        """Next to the violations, also get the total number of units as basis for the percentage scale."""
        component = self._parameter("component")
        branch = self._parameter("branch")
        base_api_url = await SonarQubeCollector._api_url(self)  # pylint: disable=protected-access
        total_metric_api_url = URL(
            f"{base_api_url}/api/measures/component?component={component}&metricKeys={self.total_metric}&"
            f"branch={branch}"
        )
        return await super()._get_source_responses(*(urls + (total_metric_api_url,)))

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        measurement = await super()._parse_source_responses(responses)
        measures: List[Dict[str, str]] = []
        for response in responses:
            measures.extend((await response.json()).get("component", {}).get("measures", []))
        measurement.total = str(sum(int(measure["value"]) for measure in measures))
        return measurement
