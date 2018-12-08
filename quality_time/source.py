"""Source base class."""

import itertools
import traceback
from typing import Optional, Sequence, Tuple

import requests
from bottle import request

from .api import API
from .type import ErrorMessage, Measurement, MeasurementResponse, URL


class Source(API):
    """Base class for metric sources."""

    TIMEOUT = 10  # Default timeout of 10 seconds

    @classmethod
    def get(cls, metric: str, urls: Sequence[URL], components: Sequence[str]) -> MeasurementResponse:
        """Connect to the source to get and parse the measurement for the metric."""
        source_responses = [cls.get_one(metric, url, component) \
                            for url, component in itertools.zip_longest(urls, components, fillvalue="")]
        return dict(request_url=request.url, source_responses=source_responses)

    @classmethod
    def get_one(cls, metric: str, url: URL, component: str) -> MeasurementResponse:
        """Return the measurement response for one source url."""
        api_url = cls.api_url(metric, url, component)
        landing_url = cls.landing_url(metric, url, component)
        response, connection_error = cls.safely_get_source_response(api_url)
        measurement, parse_error = cls.safely_parse_source_response(metric, response) if response else (None, None)
        return dict(url=url, component=component, api_url=api_url, landing_url=landing_url,
                    connection_error=connection_error, parse_error=parse_error, measurement=measurement)

    @classmethod
    def landing_url(cls, metric: str, url: URL, component: str) -> URL:  # pylint: disable=unused-argument
        """Translate the urls into the landing urls."""
        return url

    @classmethod
    def api_url(cls, metric: str, url: URL, component: str) -> URL:  # pylint: disable=unused-argument
        """Translate the url into the API url."""
        return url

    @classmethod
    def safely_get_source_response(cls, url: URL) -> Tuple[Optional[requests.Response], Optional[ErrorMessage]]:
        """Connect to the source and get the data, without failing."""
        response, error = None, None
        try:
            response = cls.get_source_response(url)
        except Exception:  # pylint: disable=broad-except
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
        except Exception:  # pylint: disable=broad-except
            error = ErrorMessage(traceback.format_exc())
        return measurement, error

    @classmethod
    # pylint: disable=unused-argument
    def parse_source_response(cls, metric: str, response: requests.Response) -> Measurement:
        """Parse the response to get the measurement for the metric."""
        return Measurement(response.text)
