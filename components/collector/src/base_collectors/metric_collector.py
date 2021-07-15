"""Metric collector base classes."""

import asyncio
from typing import Optional

import aiohttp

from collector_utilities.type import JSON
from model import MetricMeasurement

from .source_collector import SourceCollector


class MetricCollector:
    """Collect measurements for a specific metric."""

    subclasses: set[type["MetricCollector"]] = set()

    def __init__(self, session: aiohttp.ClientSession, metric, data_model: JSON) -> None:
        self.__session = session
        self.__metric = metric
        self.__data_model = data_model

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

    async def get(self) -> Optional[MetricMeasurement]:
        """Collect the measurements from the metric's sources."""
        collectors = []
        for source in self.__metric["sources"].values():
            if collector_class := SourceCollector.get_subclass(source["type"], self.__metric["type"]):
                collectors.append(collector_class(self.__session, source, self.__data_model).get())
        if not collectors:
            return None
        measurements = await asyncio.gather(*collectors)
        for measurement, source_uuid in zip(measurements, self.__metric["sources"]):
            measurement.source_uuid = source_uuid
        return MetricMeasurement(measurements)
