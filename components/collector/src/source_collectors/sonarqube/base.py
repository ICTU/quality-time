"""Base collectors for SonarQube."""

from abc import ABC

from base_collectors import SourceCollector
from collector_utilities.exceptions import CollectorError
from collector_utilities.type import URL
from model import Entities, SourceMeasurement, SourceResponses


class SonarQubeCollector(SourceCollector, ABC):
    """Base class for SonarQube collectors."""

    PAGE_SIZE = 500  # 500 is the maximum. See e.g. https://next.sonarqube.com/sonarqube/web_api/api/issues/search

    async def _get_source_responses(self, *urls: URL) -> SourceResponses:
        """Extend to check the component exists before getting data about it."""
        # SonarQube sometimes gives results (e.g. zero violations) even if the component does not exist, so we
        # check whether the component specified by the user actually exists before getting the data.
        url = await super()._api_url()
        component = self._parameter("component")
        show_component_url = URL(f"{url}/api/components/show?component={component}")
        response = (await super()._get_source_responses(show_component_url))[0]
        json = await response.json()
        if "errors" in json:
            raise CollectorError(json["errors"][0]["msg"])
        return await super()._get_source_responses(*urls)


Metrics = dict[str, str]


class SonarQubeMetricsBaseClass(SonarQubeCollector):
    """Base class for collectors that use the SonarQube measures/component API."""

    value_key = ""  # Subclass responsibility
    total_key = ""  # Subclass responsibility

    async def _landing_url(self, responses: SourceResponses) -> URL:
        """Extend to add the component measures path and parameters."""
        url = await super()._landing_url(responses)
        component = self._parameter("component")
        branch = self._parameter("branch")
        metric = self._landing_url_metric_key()
        metric_parameter = f"&metric={metric}" if metric else ""
        return URL(f"{url}/component_measures?id={component}&branch={branch}{metric_parameter}")

    def _landing_url_metric_key(self) -> str:
        """Return the metric key to use for the landing url. This can be one key or an empty string."""
        return self._metric_keys().split(",", maxsplit=1)[0]

    async def _api_url(self) -> URL:
        """Extend to add the component path and parameters."""
        url = await super()._api_url()
        component = self._parameter("component")
        branch = self._parameter("branch")
        return URL(
            f"{url}/api/measures/component?component={component}&branch={branch}&metricKeys={self._metric_keys()}",
        )

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the metrics."""
        metrics = await self.__get_metrics(responses)
        return SourceMeasurement(
            value=self._value(metrics),
            total=self._total(metrics),
            entities=await self._entities(metrics),
        )

    def _metric_keys(self) -> str:
        """Return the SonarQube metric keys to use."""
        value_key, total_key = self._value_key(), self._total_key()
        return f"{value_key},{total_key}" if total_key else value_key

    def _value(self, metrics: Metrics) -> str:
        """Return the metric value, assuming 0 when it is omitted from SonarQube api response."""
        return str(sum(int(metrics.get(key, "0")) for key in self._value_key().split(",")))

    def _total(self, metrics: Metrics) -> str:
        """Return the total value."""
        return metrics.get(self._total_key(), "100")

    async def _entities(self, metrics: Metrics) -> Entities:
        """Return the entities."""
        return Entities()

    def _value_key(self) -> str:
        """Return the SonarQube metric key(s) to use for the value. The string can be a comma-separated list of keys."""
        return self.value_key

    def _total_key(self) -> str:
        """Return the SonarQube metric key to use for the total value."""
        return self.total_key

    @staticmethod
    async def __get_metrics(responses: SourceResponses) -> Metrics:
        """Get the metric(s) from the responses."""
        measures = (await responses[0].json())["component"]["measures"]
        return {measure["metric"]: measure["value"] for measure in measures}


class SonarQubeProjectAnalysesBase(SonarQubeCollector):
    """Base class for collectors that use the SonarQube project analyses endpoint."""

    async def _api_url(self) -> URL:
        """Extend to add the project analyses path and parameters."""
        url = await super()._api_url()
        component = self._parameter("component")
        branch = self._parameter("branch")
        return URL(f"{url}/api/project_analyses/search?project={component}&branch={branch}")

    async def _landing_url(self, responses: SourceResponses) -> URL:
        """Extend to add the project activity path and parameters."""
        url = await super()._landing_url(responses)
        component = self._parameter("component")
        branch = self._parameter("branch")
        return URL(f"{url}/project/activity?id={component}&branch={branch}")
