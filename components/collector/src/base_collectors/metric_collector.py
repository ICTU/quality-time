"""Metric collector base classes."""

import asyncio
from typing import Coroutine, Optional

import aiohttp

from collector_utilities.type import JSON
from model import MetricMeasurement

from .source_collector import SourceCollector, SourceParameters


class MetricCollector:
    """Collect measurements for a specific metric."""

    subclasses: set[type["MetricCollector"]] = set()

    def __init__(self, session: aiohttp.ClientSession, metric, data_model: JSON) -> None:
        self.__session = session
        self._metric = metric
        self.__data_model = data_model
        self._parameters = {
            source_uuid: SourceParameters(source, data_model) for source_uuid, source in self._metric["sources"].items()
        }

    def __init_subclass__(cls) -> None:
        MetricCollector.subclasses.add(cls)
        super().__init_subclass__()

    @classmethod
    def get_subclass(cls, metric_type: str) -> type["MetricCollector"]:
        """Return the subclass registered for the metric type. Return this class if no subclass is found."""
        for subclass in cls.subclasses:
            if subclass.__name__.lower() == metric_type.replace("_", ""):
                return subclass
        return cls

    async def collect(self) -> Optional[MetricMeasurement]:
        """Collect the measurements from the metric's sources."""
        collectors = self.__source_collectors()
        issue_status_collector = self.__issue_status_collector()
        if not collectors and not issue_status_collector:
            return None
        if issue_status_collector:
            issue_status, *measurements = await asyncio.gather(issue_status_collector, *collectors)
        else:
            measurements = await asyncio.gather(*collectors)
            issue_status = None
        for source_measurement, source_uuid in zip(measurements, self._metric["sources"]):
            source_measurement.source_uuid = source_uuid
        return MetricMeasurement(measurements, issue_status)

    def __source_collectors(self) -> list[Coroutine]:
        """Create the source collectors for the metric."""
        collectors = []
        for source in self._metric["sources"].values():
            if collector_class := SourceCollector.get_subclass(source["type"], self._metric["type"]):
                collectors.append(collector_class(self.__session, source, self.__data_model).collect())
        return collectors

    def __issue_status_collector(self) -> Optional[Coroutine]:
        """Create the issue status collector for the metric."""
        tracker = self._metric.get("issue_tracker", {})
        tracker_type = tracker.get("type")
        issue = self._metric.get("tracker_issue")
        if issue and tracker_type and (collector_class := SourceCollector.get_subclass(tracker_type, "issue_status")):
            return collector_class(self.__session, tracker, self.__data_model).collect_issue_status(issue)
        return None
