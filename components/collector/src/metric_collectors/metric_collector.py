"""Collector base class."""

from datetime import datetime
from typing import Dict

from source_collectors.source_collector import SourceCollector
from utilities.type import Measurement


class MetricCollector:
    """Base class for collecting measurements from multiple sources for a metric."""

    def __init__(self, metric, datamodel=None) -> None:
        self.metric = metric
        self.datamodel = datamodel
        self.collectors: Dict[str, SourceCollector] = dict()
        for source_uuid, source in self.metric["sources"].items():
            collector_class = SourceCollector.get_subclass(source['type'], self.metric['type'])
            self.collectors[source_uuid] = collector_class(source, datamodel)

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

    def next_collection(self) -> datetime:
        """Return when the metric can/should be collected again."""
        return min([collector.next_collection() for collector in self.collectors.values()], default=datetime.min)

    def get(self) -> Measurement:
        """Connect to the sources to get and parse the measurements for the metric."""
        return dict(sources=[{**self.collectors[uuid].get(), "source_uuid": uuid} for uuid in self.metric["sources"]])
