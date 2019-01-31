"""Collector base class."""

import logging
import traceback
from typing import cast, Optional, Set, Tuple, Type

import cachetools
import requests

from .type import ErrorMessage, Measurement, Measurements, Response, URL


class Collector:
    """Base class for metric collectors."""

    TIMEOUT = 10  # Default timeout of 10 seconds
    RESPONSE_CACHE = cachetools.TTLCache(maxsize=256, ttl=60)  # Briefly cache responses to prevent flooding sources
    subclasses: Set[Type["Collector"]] = set()
    name = "Subclass responsibility"

    def __init__(self, metric) -> None:
        self.metric = metric

    def __init_subclass__(cls) -> None:
        Collector.subclasses.add(cls)
        super().__init_subclass__()

    @classmethod
    def get_subclass(cls, source_and_metric: str) -> Type["Collector"]:
        """Return the subclass registered for the source/metric name."""
        simplified_class_name = source_and_metric.replace("_", "")
        matching_subclasses = [sc for sc in cls.subclasses if sc.__name__.lower() == simplified_class_name]
        return matching_subclasses[0] if matching_subclasses else cls

    def get(self) -> Response:
        """Connect to the sources to get and parse the measurement for the metric."""
        metric_name = self.metric["metric"]
        source_responses = []
        for source in self.metric.get("sources", {}).values():
            collector_class = cast(Type[Collector], Collector.get_subclass(f"{source['type']}_{metric_name}"))
            source_collector = collector_class(self.metric)
            source_responses.append(source_collector.get_one(source))

        measurements = [source_response["measurement"] for source_response in source_responses]
        measurement, calculation_error = self.safely_sum(measurements)
        return dict(
            measurement=dict(calculation_error=calculation_error, measurement=measurement),
            sources=source_responses,
            metric=self.metric)

    def get_one(self, source) -> Response:
        """Return the measurement response for one source."""
        api_url = self.api_url(source)
        landing_url = self.landing_url(source)
        response, connection_error = self.safely_get_source_response(api_url)
        measurement, parse_error = self.safely_parse_source_response(response) if response else (None, None)
        return dict(name=self.name, api_url=api_url, landing_url=landing_url, measurement=measurement,
                    connection_error=connection_error, parse_error=parse_error)

    def landing_url(self, source) -> URL:  # pylint: disable=no-self-use
        """Translate the urls into the landing urls."""
        return source["url"]

    def api_url(self, source) -> URL:  # pylint: disable=no-self-use
        """Translate the url into the API url."""
        return source["url"]

    @cachetools.cached(RESPONSE_CACHE, key=lambda self, url: cachetools.keys.hashkey(url))
    def safely_get_source_response(self, url: URL) -> Tuple[Optional[requests.Response], Optional[ErrorMessage]]:
        """Connect to the source and get the data, without failing."""
        response, error = None, None
        try:
            response = self.get_source_response(url)
        except Exception:  # pylint: disable=broad-except
            error = ErrorMessage(traceback.format_exc())
        return response, error

    def get_source_response(self, url: URL) -> requests.Response:
        """Open the url. Raise an exception if the response status isn't 200 or if a time out occurs."""
        logging.info("Retrieving %s", url)
        response = requests.get(url, timeout=self.TIMEOUT)
        response.raise_for_status()
        return response

    def safely_parse_source_response(self, response: requests.Response) -> \
            Tuple[Optional[Measurement], Optional[ErrorMessage]]:
        """Parse to the measurement from the response, without failing."""
        measurement, error = None, None
        try:
            measurement = self.parse_source_response(response)
        except Exception:  # pylint: disable=broad-except
            error = ErrorMessage(traceback.format_exc())
        return measurement, error

    def parse_source_response(self, response: requests.Response) -> Measurement:
        # pylint: disable=no-self-use
        """Parse the response to get the measurement for the metric."""
        return Measurement(response.text)

    def safely_sum(self, measurements: Measurements) -> Tuple[Optional[Measurement], Optional[ErrorMessage]]:
        """Return the summation of several measurements, without failing."""
        measurement, error = None, None
        if measurements and None not in measurements:
            if len(measurements) > 1:
                try:
                    measurement = self.sum(measurements)
                except Exception:  # pylint: disable=broad-except
                    error = ErrorMessage(traceback.format_exc())
            else:
                measurement = measurements[0]
        return measurement, error

    def sum(self, measurements: Measurements) -> Measurement:  # pylint: disable=no-self-use
        """Return the summation of several measurements."""
        return Measurement(sum(int(measurement) for measurement in measurements))
