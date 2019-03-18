"""Collector base class."""

import logging
import traceback
from typing import cast, Optional, Set, Tuple, Type

import requests

from .type import ErrorMessage, Response, Units, URL, Value


def collect_measurement(metric) -> Response:
    """Connect to the sources to get and parse the measurement for the metric."""
    source_responses = []
    for source_uuid, source in metric["sources"].items():
        collector_class = cast(Type[Collector], Collector.get_subclass(f"{source['type']}_{metric['type']}"))
        source_collector = collector_class()
        source_response = source_collector.get(source)
        source_response["source_uuid"] = source_uuid
        source_responses.append(source_response)
    values = [source_response["value"] for source_response in source_responses]
    value = sum([int(value) for value in values]) if values and None not in values else None
    return dict(sources=source_responses, value=value)


class Collector:
    """Base class for metric collectors."""

    TIMEOUT = 10  # Default timeout of 10 seconds
    MAX_UNITS = 100  # The maximum number of units (e.g. violations, warnings) to send to the server
    subclasses: Set[Type["Collector"]] = set()
    request_method = "GET"  # Can be overridden to use e.g. "POST"

    def __init_subclass__(cls) -> None:
        Collector.subclasses.add(cls)
        super().__init_subclass__()

    @classmethod
    def get_subclass(cls, source_and_metric: str) -> Type["Collector"]:
        """Return the subclass registered for the source/metric name."""
        simplified_class_name = source_and_metric.replace("_", "")
        matching_subclasses = [sc for sc in cls.subclasses if sc.__name__.lower() == simplified_class_name]
        return matching_subclasses[0] if matching_subclasses else cls

    def get(self, source) -> Response:
        """Return the measurement response for one source."""
        parameters = source.get("parameters", {})
        api_url = self.api_url(**parameters)
        landing_url = self.landing_url(**parameters)
        response, connection_error = self.safely_get_source_response(api_url, **parameters)
        value, units, parse_error = self.safely_parse_source_response(response, **parameters)
        return dict(api_url=api_url, landing_url=landing_url, value=value, units=units,
                    connection_error=connection_error, parse_error=parse_error)

    def landing_url(self, **parameters) -> URL:  # pylint: disable=no-self-use
        """Translate the urls into the landing urls."""
        return parameters.get("url", "")

    def api_url(self, **parameters) -> URL:  # pylint: disable=no-self-use
        """Translate the url into the API url."""
        return parameters.get("url", "")

    def safely_get_source_response(
            self, api_url: URL, **parameters) -> Tuple[Optional[requests.Response], ErrorMessage]:
        """Connect to the source and get the data, without failing. This method should not be overridden
        because it makes sure the collection of source data never causes the collector to fail."""
        logging.info("Retrieving %s", api_url)
        response, error = None, None
        try:
            response = self.get_source_response(api_url, **parameters)
        except Exception:  # pylint: disable=broad-except
            error = traceback.format_exc()
        return response, error

    def get_source_response(self, api_url: URL, **parameters) -> requests.Response:
        """Open the url. Raise an exception if the response status isn't 200 or if a time out occurs.
        This method can be overridden by collectors that need a different way to retrieve the source data."""
        username, password = parameters.get("username", ""), parameters.get("password", "")
        basic_auth_credentials = (username, password) if username or password else None
        if self.request_method == "GET":
            response = requests.get(api_url, timeout=self.TIMEOUT, auth=basic_auth_credentials)
        else:
            response = requests.post(api_url, timeout=self.TIMEOUT, auth=basic_auth_credentials)
        response.raise_for_status()
        return response

    def safely_parse_source_response(
            self, response: Optional[requests.Response], **parameters) -> Tuple[Value, Units, ErrorMessage]:
        """Parse the data from the response, without failing. This method should not be overridden because it
        makes sure that the parsing of source data never causes the collector to fail."""
        units: Units = []
        value, error = None, None
        if response:
            try:
                value = self.parse_source_response_value(response, **parameters)
                units = self.parse_source_response_units(response, **parameters)
            except Exception:  # pylint: disable=broad-except
                error = traceback.format_exc()
        return value, units[:self.MAX_UNITS], error

    def parse_source_response_value(self, response: requests.Response, **parameters) -> Value:
        # pylint: disable=no-self-use,unused-argument
        """Parse the response to get the measurement for the metric. This method can be overridden by collectors
        to parse the retrieved sources data."""
        return str(response.text)  # pragma: nocover

    def parse_source_response_units(self, response: requests.Response, **parameters) -> Units:
        # pylint: disable=no-self-use,unused-argument
        """Parse the response to get the units (e.g. violations, test cases, user stories) for the metric.
        This method can to be overridden by collectors when a source can provide the metric units."""
        return []
