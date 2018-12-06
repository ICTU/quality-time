import itertools
import sys
import traceback
from typing import Optional, Sequence, Tuple

import requests

from quality_time.metric import Metric
from .type import ErrorMessage, Measurement, MeasurementResponse, URL


class Source:
    """Base class for metric sources."""

    TIMEOUT = 10  # Default timeout of 10 seconds

    @classmethod
    def get(cls, metric: Metric, urls: Sequence[URL], components: Sequence[str]) -> MeasurementResponse:
        """Connect to the source to get and parse the measurement for the metric."""
        source_metric = cls.convert_metric_name(metric)
        source_responses = [cls.get_one(source_metric, url, component) \
                            for url, component in itertools.zip_longest(urls, components)]
        measurements = [source_response["measurement"] for source_response in source_responses]
        measurement, calculation_error = metric.safely_sum(measurements)
        return dict(source=cls.name(), metric=metric.name(), source_metric=source_metric, 
                    source_responses=source_responses, calculation_error=calculation_error, measurement=measurement)
                
    @classmethod
    def get_one(cls, source_metric: str, url: URL, component: str) -> MeasurementResponse:
        """Return the measurement response for one source url."""
        api_url = cls.api_url(source_metric, url, component)
        landing_url = cls.landing_url(source_metric, url, component) 
        response, connection_error = cls.safely_get_source_response(api_url)
        measurement, parse_error = cls.safely_parse_source_response(source_metric, response) \
            if response else (None, None)
        return dict(url=url, component=component, api_url=api_url, landing_url=landing_url, 
                    connection_error=connection_error, parse_error=parse_error, measurement=measurement)

    @classmethod
    def name(cls) -> str:
        return cls.__name__

    @classmethod
    def convert_metric_name(cls, metric: Metric) -> str:
        """Convert the generic metric name in the source specific version of the metric name."""
        return metric.name().lower()

    @classmethod
    def landing_url(cls, metric: str, url: URL, component: str) -> URL: 
        """Translate the urls into the landing urls.""" 
        return url

    @classmethod
    def api_url(cls, metric: str, url: URL, component: str) -> URL: 
        """Translate the url into the API url.""" 
        return url

    @classmethod
    def safely_get_source_response(cls, url: URL) -> Tuple[Optional[requests.Response], Optional[ErrorMessage]]:
        """Connect to the source and get the data, without failing.""" 
        response, error = None, None
        try:
            response = cls.get_source_response(url)
        except Exception:
            error = ErrorMessage(traceback.format_exc())
        return response, error

    @classmethod 
    def get_source_response(cls, url: URL) -> requests.Response:
        """Open the url. Raise an exception if the response status isn't 200 or if a time out occurs."""
        response = requests.get(url, timeout=cls.TIMEOUT)
        response.raise_for_status()
        return response

    @classmethod
    def safely_parse_source_response(cls, metric: str, response: requests.Response) -> \
            Tuple[Optional[Measurement], Optional[ErrorMessage]]:
        """Parse to the measurement from the response, without failing.""" 
        measurement, error = None, None
        try:
            measurement = cls.parse_source_response(metric, response) 
        except Exception:
            error = ErrorMessage(traceback.format_exc())
        return measurement, error

    @classmethod 
    def parse_source_response(cls, metric: str, response: requests.Response) -> Measurement:
        """Parse the response to get the measurement for the metric."""
        return Measurement(response.text)
