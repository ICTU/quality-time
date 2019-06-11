"""Collector base class."""

import logging
import traceback
from datetime import datetime, timedelta
from typing import cast, Dict, List, Optional, Set, Tuple, Type

import requests

from .type import ErrorMessage, Response, Entities, Parameter, URL, Value
from .util import stable_traceback


class MetricCollector:
    """Base class for collecting measurements from multiple sources for a metric."""

    def __init__(self, metric) -> None:
        self.metric = metric
        self.collectors: Dict[str, Collector] = dict()
        for source_uuid, source in self.metric["sources"].items():
            collector_class = cast(Type[Collector], Collector.get_subclass(source['type'], self.metric['type']))
            self.collectors[source_uuid] = collector_class(source)

    def can_collect(self) -> bool:
        """Return whether the user has specified enough information to measure this metric."""
        sources = self.metric.get("sources")
        return any(source.get("parameters", {}).get("url") or (source["type"] in ("calendar", "random"))
                   for source in sources.values()) if sources else False

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
        add = dict(sum=sum, max=max)[self.metric.get("addition", "sum")]
        value = add([int(value) for value in values]) if (values and None not in values) else None  # type: ignore
        return dict(sources=source_responses, value=value)


class Collector:
    """Base class for source collectors."""

    TIMEOUT = 10  # Default timeout of 10 seconds
    MAX_ENTITIES = 100  # The maximum number of entities (e.g. violations, warnings) to send to the server
    subclasses: Set[Type["Collector"]] = set()

    def __init__(self, source) -> None:
        self.source = source
        self.parameters: Dict[str, str] = source.get("parameters", {})

    def __init_subclass__(cls) -> None:
        Collector.subclasses.add(cls)
        super().__init_subclass__()

    @classmethod
    def get_subclass(cls, source_type: str, metric_type: str) -> Type["Collector"]:
        """Return the subclass registered for the source/metric name. First try to find a match on both source type
        and metric type. If no match is found, return the generic collector for the source type."""
        for class_name in (f"{source_type}{metric_type}", source_type):
            matching_subclasses = [sc for sc in cls.subclasses if sc.__name__.lower() == class_name.replace("_", "")]
            if matching_subclasses:
                return matching_subclasses[0]
        raise LookupError(f"Couldn't find collector subclass for source {source_type} and metric {metric_type}")

    def get(self) -> Response:
        """Return the measurement response for one source."""
        api_url = self.api_url(**self.parameters)
        responses, connection_error = self.safely_get_source_responses(api_url, **self.parameters)
        value, entities, parse_error = self.safely_parse_source_responses(responses, **self.parameters)
        landing_url = self.landing_url(responses, **self.parameters)
        return dict(api_url=api_url, landing_url=landing_url, value=value, entities=entities,
                    connection_error=connection_error, parse_error=parse_error)

    def landing_url(self, responses: List[requests.Response], **parameters: Parameter) -> URL:  # pylint: disable=no-self-use,unused-argument
        """Translate the url parameter into the landing url."""
        url = cast(str, parameters.get("url", "")).strip("/")
        return URL(url[:-(len("xml"))] + "html" if url.endswith(".xml") else url)

    def api_url(self, **parameters: Parameter) -> URL:  # pylint: disable=no-self-use
        """Translate the url parameter into the API url."""
        return URL(cast(str, parameters.get("url", "")).strip("/"))

    def safely_get_source_responses(
            self, api_url: URL, **parameters: Parameter) -> Tuple[List[requests.Response], ErrorMessage]:
        """Connect to the source and get the data, without failing. This method should not be overridden
        because it makes sure the collection of source data never causes the collector to fail."""
        logging.info("Retrieving %s", api_url)
        responses: List[requests.Response] = []
        error = None
        try:
            responses = self.get_source_responses(api_url, **parameters)
            for response in responses:
                response.raise_for_status()
        except Exception:  # pylint: disable=broad-except
            error = stable_traceback(traceback.format_exc())
        return responses, error

    def get_source_responses(self, api_url: URL, **parameters: Parameter) -> List[requests.Response]:
        """Open the url. Can be overridden if a post request is needed or multiple requests need to be made."""
        return [requests.get(api_url, timeout=self.TIMEOUT, auth=self.basic_auth_credentials(**parameters))]

    @staticmethod
    def basic_auth_credentials(**parameters: Parameter) -> Optional[Tuple[str, str]]:
        """Return the basic authentication credentials, if any."""
        token = cast(str, parameters.get("private_token", ""))
        if token:
            return (token, "")
        username, password = cast(str, parameters.get("username", "")), cast(str, parameters.get("password", ""))
        return (username, password) if username and password else None

    def safely_parse_source_responses(
            self, responses: List[requests.Response], **parameters: Parameter) -> Tuple[Value, Entities, ErrorMessage]:
        """Parse the data from the responses, without failing. This method should not be overridden because it
        makes sure that the parsing of source data never causes the collector to fail."""
        entities: Entities = []
        value, error = None, None
        if responses:
            try:
                value = self.parse_source_responses_value(responses, **parameters)
                entities = self.parse_source_responses_entities(responses, **parameters)
            except Exception:  # pylint: disable=broad-except
                error = stable_traceback(traceback.format_exc())
        return value, entities[:self.MAX_ENTITIES], error

    def parse_source_responses_value(self, responses: List[requests.Response], **parameters: Parameter) -> Value:
        # pylint: disable=no-self-use,unused-argument
        """Parse the responses to get the measurement for the metric. This method can be overridden by collectors
        to parse the retrieved sources data."""
        return str(responses[0].text)

    def parse_source_responses_entities(self, responses: List[requests.Response], **parameters: Parameter) -> Entities:
        # pylint: disable=no-self-use,unused-argument
        """Parse the response to get the entities (e.g. violation, test cases, user stories) for the metric.
        This method can to be overridden by collectors when a source can provide the measured entities."""
        return []

    def next_collection(self) -> datetime:  # pylint: disable=no-self-use
        """Return when this source should be connected again for measurement data."""
        return datetime.now() + timedelta(seconds=15 * 60)
