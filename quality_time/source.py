"""Source base class."""

import itertools
import logging
import traceback
from typing import Optional, Tuple

import cachetools
import requests

from .api import API
from .type import ErrorMessage, Measurement, Response, URL


class Source(API):
    """Base class for metric sources."""

    TIMEOUT = 10  # Default timeout of 10 seconds
    RESPONSE_CACHE = cachetools.TTLCache(maxsize=256, ttl=60)  # Briefly cache responses to prevent flooding sources
    name = "Subclass responsibility"

    def get(self, response: Response) -> Response:  # pylint: disable=unused-argument
        """Connect to the source to get and parse the measurement for the metric."""
        source_response = response.copy() if response else dict()
        urls = response.get("urls", [])
        components = response.get("components", [])
        source_response["source"] = self.name
        source_response["source_responses"] = [self.get_one(url, component) for url, component in
                                               itertools.zip_longest(urls, components, fillvalue="")]
        return source_response

    def get_one(self, url: URL, component: str) -> Response:
        """Return the measurement response for one source url."""
        api_url = self.api_url(url, component)
        landing_url = self.landing_url(url, component)
        response, connection_error = self.safely_get_source_response(api_url)
        measurement, parse_error = self.safely_parse_source_response(response) if response else (None, None)
        return dict(api_url=api_url, landing_url=landing_url, measurement=measurement,
                    connection_error=connection_error, parse_error=parse_error)

    def landing_url(self, url: URL, component: str) -> URL:  # pylint: disable=unused-argument,no-self-use
        """Translate the urls into the landing urls."""
        return url

    def api_url(self, url: URL, component: str) -> URL:  # pylint: disable=unused-argument,no-self-use
        """Translate the url into the API url."""
        return url

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
