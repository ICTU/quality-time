"""Source collector base class."""

import logging
import traceback
from datetime import datetime, timedelta
from typing import cast, Dict, List, Optional, Set, Tuple, Type

import requests

from .type import ErrorMessage, Response, Entities, URL, Value
from .util import stable_traceback


class SourceCollector:
    """Base class for source collectors. Source collectors are subclasses of this class that know how to collect the
    measurement data for one specific metric from one specific source."""

    TIMEOUT = 10  # Default timeout of 10 seconds
    MAX_ENTITIES = 100  # The maximum number of entities (e.g. violations, warnings) to send to the server
    subclasses: Set[Type["SourceCollector"]] = set()

    def __init__(self, source) -> None:
        self.source = source
        self.parameters: Dict[str, str] = source.get("parameters", {})

    def __init_subclass__(cls) -> None:
        SourceCollector.subclasses.add(cls)
        super().__init_subclass__()

    @classmethod
    def get_subclass(cls, source_type: str, metric_type: str) -> Type["SourceCollector"]:
        """Return the subclass registered for the source/metric name. First try to find a match on both source type
        and metric type. If no match is found, return the generic collector for the source type."""
        for class_name in (f"{source_type}{metric_type}", source_type):
            matching_subclasses = [sc for sc in cls.subclasses if sc.__name__.lower() == class_name.replace("_", "")]
            if matching_subclasses:
                return matching_subclasses[0]
        raise LookupError(f"Couldn't find collector subclass for source {source_type} and metric {metric_type}")

    def get(self) -> Response:
        """Return the measurement response for one source."""
        api_url = self.api_url()
        responses, connection_error = self.safely_get_source_responses(api_url)
        value, entities, parse_error = self.safely_parse_source_responses(responses)
        landing_url = self.landing_url(responses)
        return dict(api_url=api_url, landing_url=landing_url, value=value, entities=entities,
                    connection_error=connection_error, parse_error=parse_error)

    def landing_url(self, responses: List[requests.Response]) -> URL:  # pylint: disable=no-self-use,unused-argument
        """Translate the url parameter into the landing url."""
        url = cast(str, self.parameters.get("url", "")).strip("/")
        return URL(url[:-(len("xml"))] + "html" if url.endswith(".xml") else url)

    def api_url(self) -> URL:  # pylint: disable=no-self-use
        """Translate the url parameter into the API url."""
        return URL(cast(str, self.parameters.get("url", "")).strip("/"))

    def safely_get_source_responses(self, api_url: URL) -> Tuple[List[requests.Response], ErrorMessage]:
        """Connect to the source and get the data, without failing. This method should not be overridden
        because it makes sure the collection of source data never causes the collector to fail."""
        logging.info("Retrieving %s", api_url or self.__class__.__name__)
        responses: List[requests.Response] = []
        error = None
        try:
            responses = self.get_source_responses(api_url)
            for response in responses:
                response.raise_for_status()
        except Exception:  # pylint: disable=broad-except
            error = stable_traceback(traceback.format_exc())
        return responses, error

    def get_source_responses(self, api_url: URL) -> List[requests.Response]:
        """Open the url. Can be overridden if a post request is needed or multiple requests need to be made."""
        return [requests.get(api_url, timeout=self.TIMEOUT, auth=self.basic_auth_credentials())]

    def basic_auth_credentials(self) -> Optional[Tuple[str, str]]:
        """Return the basic authentication credentials, if any."""
        token = cast(str, self.parameters.get("private_token", ""))
        if token:
            return (token, "")
        username = cast(str, self.parameters.get("username", ""))
        password = cast(str, self.parameters.get("password", ""))
        return (username, password) if username and password else None

    def safely_parse_source_responses(self, responses: List[requests.Response]) -> Tuple[Value, Entities, ErrorMessage]:
        """Parse the data from the responses, without failing. This method should not be overridden because it
        makes sure that the parsing of source data never causes the collector to fail."""
        entities: Entities = []
        value, error = None, None
        if responses:
            try:
                value = self.parse_source_responses_value(responses)
                entities = self.parse_source_responses_entities(responses)
            except Exception:  # pylint: disable=broad-except
                error = stable_traceback(traceback.format_exc())
        return value, entities[:self.MAX_ENTITIES], error

    def parse_source_responses_value(self, responses: List[requests.Response]) -> Value:
        # pylint: disable=no-self-use,unused-argument
        """Parse the responses to get the measurement for the metric. This method can be overridden by collectors
        to parse the retrieved sources data."""
        return str(responses[0].text)

    def parse_source_responses_entities(self, responses: List[requests.Response]) -> Entities:
        # pylint: disable=no-self-use,unused-argument
        """Parse the response to get the entities (e.g. violation, test cases, user stories) for the metric.
        This method can to be overridden by collectors when a source can provide the measured entities."""
        return []

    def next_collection(self) -> datetime:  # pylint: disable=no-self-use
        """Return when this source should be connected again for measurement data."""
        return datetime.now() + timedelta(seconds=15 * 60)
