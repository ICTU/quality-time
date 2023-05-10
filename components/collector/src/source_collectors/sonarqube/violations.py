"""SonarQube violations collector."""

from shared_data_model import DATA_MODEL

from collector_utilities.type import URL
from model import Entities, Entity, SourceMeasurement, SourceResponses

from .base import SonarQubeCollector


class SonarQubeViolations(SonarQubeCollector):
    """SonarQube violations metric. Also base class for metrics that measure specific rules."""

    rules_configuration = ""  # Subclass responsibility
    types_parameter = "types"

    async def _landing_url(self, responses: SourceResponses) -> URL:
        """Extend to add the issues path and parameters."""
        url = await super()._landing_url(responses)
        component = self._parameter("component")
        branch = self._parameter("branch")
        landing_url = f"{url}/project/issues?id={component}&branch={branch}&resolved=false"
        return URL(
            landing_url
            + self._query_parameter("severities")
            + self._query_parameter(self.types_parameter)
            + self.__rules_url_parameter(),
        )

    async def _api_url(self) -> URL:
        """Extend to add the issue search path and parameters."""
        url = await super()._api_url()
        component = self._parameter("component")
        branch = self._parameter("branch")
        # If there's more than 500 issues only the first 500 are returned. This is no problem since we limit
        # the number of "entities" sent to the server anyway (that limit is 100 currently).
        api = f"{url}/api/issues/search?componentKeys={component}&branch={branch}&resolved=false&ps=500"
        return URL(
            api
            + self._query_parameter("severities")
            + self._query_parameter(self.types_parameter)
            + self.__rules_url_parameter(),
        )

    def _query_parameter(self, parameter_key: str) -> str:
        """Return the multiple choice parameter as query parameter that can be passed to SonarQube."""
        values = ",".join(value.upper() for value in sorted(self._parameter(parameter_key)))
        return "" if values == self.__default_value(parameter_key) else f"&{parameter_key}={values}"

    def __rules_url_parameter(self) -> str:
        """Return the rules url parameter, if any."""
        rules = (
            DATA_MODEL.sources[self.source_type].configuration[self.rules_configuration].value
            if self.rules_configuration
            else []
        )
        return f"&rules={','.join(rules)}" if rules else ""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the issues."""
        value = 0
        entities = Entities()
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
        return URL(f"{url}/project/issues?id={component}&branch={branch}&issues={issue_key}&open={issue_key}")

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

    def __default_value(self, parameter_key: str) -> str:
        """Return the default value for the parameter."""
        defaults = DATA_MODEL.sources[self.source_type].parameters[parameter_key].values or []
        return ",".join(value.upper() for value in sorted(defaults))


class SonarQubeViolationsWithPercentageScale(SonarQubeViolations):
    """SonarQube violations collectors that support the percentage scale."""

    total_metric = ""  # Subclass responsibility

    async def _get_source_responses(self, *urls: URL) -> SourceResponses:
        """Extend to, next to the violations, get the total number of violations as basis for the percentage scale."""
        component = self._parameter("component")
        branch = self._parameter("branch")
        base_api_url = await SonarQubeCollector._api_url(self)  # noqa: SLF001
        total_metric_api_url = URL(
            f"{base_api_url}/api/measures/component?component={component}&branch={branch}"
            f"&metricKeys={self.total_metric}",
        )
        return await super()._get_source_responses(*([*urls, total_metric_api_url]))

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Extend to parse the total number of violations."""
        measurement = await super()._parse_source_responses(responses)
        measures: list[dict[str, str]] = []
        for response in responses:
            measures.extend((await response.json()).get("component", {}).get("measures", []))
        measurement.total = str(sum(int(measure["value"]) for measure in measures))
        return measurement
