"""Collector base class."""

import asyncio
from typing import Final, List

import aiohttp

from source_collectors.source_collector import SourceCollector
from collector_utilities.type import Measurement


class MetricCollector:
    """Base class for collecting measurements from multiple sources for a metric."""

    def __init__(self, session: aiohttp.ClientSession, metric, data_model=None) -> None:
        self.metric: Final = metric
        self.datamodel: Final = data_model
        self.collectors: List[SourceCollector] = []
        for source in self.metric["sources"].values():
            collector_class = SourceCollector.get_subclass(source["type"], self.metric["type"])
            self.collectors.append(collector_class(session, source, data_model))

    def can_collect(self) -> bool:
        """Return whether the user has specified all mandatory parameters for all sources."""
        sources = self.metric.get("sources")
        for source in sources.values():
            parameters = self.datamodel.get("sources", {}).get(source["type"], {}).get("parameters", {})
            for parameter_key, parameter in parameters.items():
                if parameter.get("mandatory") and self.metric["type"] in parameter.get("metrics") and \
                        not source.get("parameters", {}).get(parameter_key):
                    return False
        return bool(sources)

    async def get(self) -> Measurement:
        """Connect to the sources to get and parse the measurements for the metric."""
        measurements = await asyncio.gather(*[collector.get() for collector in self.collectors])
        for measurement, source_uuid in zip(measurements, self.metric["sources"]):
            measurement["source_uuid"] = source_uuid
        return dict(sources=measurements)
