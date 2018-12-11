"""Source base class."""

import itertools
import traceback
from typing import Optional, Tuple

import requests

from .api import API
from .type import ErrorMessage, Measurement, MeasurementResponse, URL


class Source(API):
    """Base class for metric sources."""

    TIMEOUT = 10  # Default timeout of 10 seconds

    def get(self, metric: str) -> MeasurementResponse:
        """Connect to the source to get and parse the measurement for the metric."""
        source_responses = [self.get_one(metric, url, component) for url, component in \
                            itertools.zip_longest(self.request.query.getall("url"),
                                                  self.request.query.getall("component"), fillvalue="")]
        return dict(request_url=self.request.url, source_responses=source_responses)

    def get_one(self, metric: str, url: URL, component: str) -> MeasurementResponse:
        """Return the measurement response for one source url."""
        api_url = self.api_url(metric, url, component)
        landing_url = self.landing_url(metric, url, component)
        response, connection_error = self.safely_get_source_response(api_url)
        measurement, parse_error = self.safely_parse_source_response(metric, response) if response else (None, None)
        return dict(api_url=api_url, landing_url=landing_url, measurement=measurement,
                    connection_error=connection_error, parse_error=parse_error)

    def landing_url(self, metric: str, url: URL, component: str) -> URL:  # pylint: disable=unused-argument,no-self-use
        """Translate the urls into the landing urls."""
        return url

    def api_url(self, metric: str, url: URL, component: str) -> URL:  # pylint: disable=unused-argument,no-self-use
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
