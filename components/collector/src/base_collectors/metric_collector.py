"""Metric collector base classes."""

import asyncio
from collections.abc import Coroutine

import aiohttp

from shared_data_model import DATA_MODEL

from model import MetricMeasurement

from .source_collector import SourceCollector, SourceParameters


class MetricCollector:
    """Collect measurements for a specific metric."""

    subclasses: set[type["MetricCollector"]] = set()

    def __init__(self, session: aiohttp.ClientSession, metric) -> None:
        self.__session = session
        self._metric = metric
        self._parameters = {
            source_uuid: SourceParameters(source) for source_uuid, source in self._metric["sources"].items()
        }

    def __init_subclass__(cls) -> None:
        """Register the subclass as metric collector."""
        MetricCollector.subclasses.add(cls)
        super().__init_subclass__()

    @classmethod
    def get_subclass(cls, metric_type: str) -> type["MetricCollector"]:
        """Return the subclass registered for the metric type. Return this class if no subclass is found."""
        for subclass in cls.subclasses:
            if subclass.__name__.lower() == metric_type.replace("_", ""):
                return subclass
        return cls

    async def collect(self) -> MetricMeasurement | None:
        """Collect the measurements from the metric's sources."""
        source_collectors = self.__source_collectors()
        issue_status_collectors = self.__issue_status_collectors()
        if not source_collectors and not issue_status_collectors:
            return None
        measurements = await asyncio.gather(*source_collectors)
        for source_measurement, source_uuid in zip(measurements, self._metric["sources"], strict=True):
            source_measurement.source_uuid = source_uuid
        issue_statuses = await asyncio.gather(*issue_status_collectors)
        return MetricMeasurement(measurements, issue_statuses)

    def __source_collectors(self) -> list[Coroutine]:
        """Create the source collectors for the metric."""
        collectors = []
        for source in self._metric["sources"].values():
            if not self.__has_all_mandatory_parameters(source):
                return []
            if collector_class := SourceCollector.get_subclass(source["type"], self._metric["type"]):
                collectors.append(collector_class(self.__session, source).collect())
        return collectors

    def __issue_status_collectors(self) -> list[Coroutine]:
        """Create the issue status collector for the metric."""
        tracker = self._metric.get("issue_tracker", {})
        tracker_type = tracker.get("type")
        has_tracker = bool(tracker_type and tracker.get("parameters", {}).get("url"))
        if has_tracker and (collector_class := SourceCollector.get_subclass(tracker_type, "issue_status")):
            return [
                collector_class(self.__session, tracker).collect_issue_status(issue_id)
                for issue_id in self._metric.get("issue_ids", [])
            ]
        return []

    def __has_all_mandatory_parameters(self, source) -> bool:
        """Return whether the user has specified all mandatory parameters for the source."""
        try:
            parameters = DATA_MODEL.sources[source["type"]].parameters
        except KeyError:
            # This can happen if the source type has been removed from the data model, problem will be logged elsewhere
            return True
        for parameter_key, parameter in parameters.items():
            if (
                parameter.mandatory
                and self._metric["type"] in parameter.metrics
                and not source.get("parameters", {}).get(parameter_key)
                and not parameter.default_value
            ):
                return False
        return True
