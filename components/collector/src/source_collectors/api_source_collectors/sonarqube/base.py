"""Base collectors for SonarQube."""

from abc import ABC
from typing import Dict, List

from base_collectors import SourceCollector, SourceCollectorException
from collector_utilities.type import URL
from source_model import Entity, SourceMeasurement, SourceResponses


class SonarQubeCollector(SourceCollector, ABC):  # skipqc: PYL-W0223
    """Base class for SonarQube collectors."""

    async def _get_source_responses(self, *urls: URL) -> SourceResponses:
        """Extend to check the component exists before getting data about it."""
        # SonarQube sometimes gives results (e.g. zero violations) even if the component does not exist, so we
        # check whether the component specified by the user actually exists before getting the data.
        url = await SourceCollector._api_url(self)
        component = self._parameter("component")
        show_component_url = URL(f"{url}/api/components/show?component={component}")
        response = (await super()._get_source_responses(show_component_url))[0]
        json = await response.json()
        if "errors" in json:
            raise SourceCollectorException(json["errors"][0]["msg"])
        return await super()._get_source_responses(*urls)


class SonarQubeMetricsBaseClass(SonarQubeCollector):
    """Base class for collectors that use the SonarQube measures/component API."""

    valueKey = ""  # Subclass responsibility
    totalKey = ""  # Subclass responsibility

    async def _landing_url(self, responses: SourceResponses) -> URL:
        """Extend to add the component measures path and parameters."""
        url = await super()._landing_url(responses)
        component = self._parameter("component")
        branch = self._parameter("branch")
        metric = self._landing_url_metric_key()
        metric_parameter = f"&metric={metric}" if metric else ""
        return URL(f"{url}/component_measures?id={component}{metric_parameter}&branch={branch}")

    def _landing_url_metric_key(self) -> str:
        """Return the metric key to use for the landing url. This can be one key or an empty string."""
        return self._metric_keys().split(",")[0]

    async def _api_url(self) -> URL:
        """Extend to add the component path and parameters."""
        url = await super()._api_url()
        component = self._parameter("component")
        branch = self._parameter("branch")
        return URL(
            f"{url}/api/measures/component?component={component}&metricKeys={self._metric_keys()}&branch={branch}"
        )

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the metrics."""
        metrics = await self.__get_metrics(responses)
        return SourceMeasurement(
            value=self._value(metrics), total=self._total(metrics), entities=await self._entities(metrics)
        )

    def _metric_keys(self) -> str:
        """Return the SonarQube metric keys to use."""
        value_key, total_key = self._value_key(), self._total_key()
        return f"{value_key},{total_key}" if total_key else value_key

    def _value(self, metrics: Dict[str, str]) -> str:
        """Return the metric value."""
        return str(sum(int(metrics[key]) for key in self._value_key().split(",")))

    def _total(self, metrics: Dict[str, str]) -> str:
        """Return the total value."""
        return metrics.get(self._total_key(), "100")

    async def _entities(self, metrics: Dict[str, str]) -> List[Entity]:  # pylint: disable=no-self-use,unused-argument
        """Return the entities."""
        return []

    def _value_key(self) -> str:
        """Return the SonarQube metric key(s) to use for the value. The string can be a comma-separated list of keys."""
        return self.valueKey

    def _total_key(self) -> str:
        """Return the SonarQube metric key to use for the total value."""
        return self.totalKey

    @staticmethod
    async def __get_metrics(responses: SourceResponses) -> Dict[str, str]:
        """Get the metric(s) from the responses."""
        measures = (await responses[0].json())["component"]["measures"]
        return {measure["metric"]: measure["value"] for measure in measures}
