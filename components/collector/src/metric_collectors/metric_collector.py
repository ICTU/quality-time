"""Collector base class."""

from datetime import datetime
from typing import cast, Dict, Type

from source_collectors.source_collector import SourceCollector
from utilities.type import Response


class MetricCollector:
    """Base class for collecting measurements from multiple sources for a metric."""

    def __init__(self, metric, datamodel=None) -> None:
        self.metric = metric
        self.datamodel = datamodel
        self.collectors: Dict[str, SourceCollector] = dict()
        for source_uuid, source in self.metric["sources"].items():
            collector_class = cast(
                Type[SourceCollector], SourceCollector.get_subclass(source['type'], self.metric['type']))
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

    def get(self) -> Response:
        """Connect to the sources to get and parse the measurement for the metric."""
        source_responses = []
        for source_uuid in self.metric["sources"]:
            source_response = self.collectors[source_uuid].get()
            source_response["source_uuid"] = source_uuid
            source_responses.append(source_response)
        values = [source_response["value"] for source_response in source_responses]
        add = dict(sum=sum, max=max, min=min)[self.metric.get("addition", "sum")]
        value = add([int(value) for value in values]) if (values and None not in values) else None  # type: ignore
        return dict(sources=source_responses, value=value)
