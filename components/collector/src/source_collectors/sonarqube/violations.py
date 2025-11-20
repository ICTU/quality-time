"""SonarQube violations collector."""

from typing import cast
from urllib.parse import urlparse

from shared_data_model import DATA_MODEL

from collector_utilities.type import URL
from model import Entities, Entity, SourceMeasurement, SourceResponses

from .base import SonarQubeCollector


class SonarQubeViolations(SonarQubeCollector):
    """SonarQube violations metric. Also base class for metrics that measure specific rules."""

    rules_configuration = ""  # Subclass responsibility

    async def _landing_url(self, responses: SourceResponses) -> URL:
        """Extend to add the issues path and parameters."""
        url = await super()._landing_url(responses)
        component = self._parameter("component")
        branch = self._parameter("branch")
        landing_url = f"{url}/project/issues?id={component}&branch={branch}&resolved=false"
        if directories := self._parameter("directories_to_include"):
            landing_url += f"&directories={','.join(sorted(directories))}"
        return URL(landing_url + self._url_parameters())

    async def _api_url(self) -> URL:
        """Extend to add the issue search path and parameters."""
        url = await super()._api_url()
        component = self._parameter("component")
        branch = self._parameter("branch")
        # If there's more than 500 issues only the first 500 are returned. This is no problem since we limit
        # the number of "entities" sent to the server anyway (that limit is 250 currently).
        # Issue: https://github.com/ICTU/quality-time/issues/11004
        api = f"{url}/api/issues/search?projects={component}&branch={branch}&resolved=false&ps={self.PAGE_SIZE}"
        if directories := self._parameter("directories_to_include"):
            key = "componentKeys" if urlparse(url).hostname == "sonarcloud.io" else "components"
            directory_keys = [f"{component}:{directory}" for directory in directories]
            api += f"&{key}={','.join(sorted(directory_keys))}"
        return URL(api + self._url_parameters())

    def _url_parameters(self) -> str:
        """Return the parameters common to the API URL and the landing URL."""
        return (
            self._query_parameter("impact_severities", uppercase=True)
            + self._query_parameter("impacted_software_qualities", uppercase=True)
            + self._query_parameter("clean_code_attribute_categories", uppercase=True)
            + self._query_parameter("tags")
            + self.__rules_url_parameter()
        )

    def _query_parameter(self, parameter_key: str, uppercase: bool = False) -> str:
        """Return the multiple choice parameter as query parameter that can be passed to SonarQube."""
        parameter_value = ",".join(sorted(cast(list[str], self._parameter(parameter_key))))
        if uppercase:
            parameter_value = parameter_value.upper()
        quality_time_parameter_to_sonarqube_query_parameter_mapping = {
            "impact_severities": "impactSeverities",
            "impacted_software_qualities": "impactSoftwareQualities",
            "clean_code_attribute_categories": "cleanCodeAttributeCategories",
        }
        query_parameter = quality_time_parameter_to_sonarqube_query_parameter_mapping.get(parameter_key, parameter_key)
        return "" if parameter_value == self.__default_value(parameter_key) else f"&{query_parameter}={parameter_value}"

    def __rules_url_parameter(self) -> str:
        """Return the rules URL parameter, if any."""
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
        impacts = [
            f"{impact['severity']} impact on {impact['softwareQuality']}".lower() for impact in issue.get("impacts", [])
        ]
        return Entity(
            key=issue["key"],
            url=await self.__issue_landing_url(issue["key"]),
            message=issue["message"],
            impacts=", ".join(impacts),
            clean_code_attribute_category=issue["cleanCodeAttributeCategory"].lower(),
            component=issue["component"],
            creation_date=issue["creationDate"],
            update_date=issue["updateDate"],
            tags=", ".join(sorted(issue.get("tags", []))),
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
        # Note that the SonarQube api sometimes omits values (when they are 0) from the component measurement endpoint
        # This has not (yet) been observed for the 'functions' metric and current code would iterate over an empty list
        measurement.total = str(sum(int(measure["value"]) for measure in measures))
        return measurement
