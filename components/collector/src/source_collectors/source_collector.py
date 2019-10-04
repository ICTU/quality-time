"""Source collector base class."""

import logging
import traceback
import urllib
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from typing import cast, Dict, List, Optional, Set, Tuple, Type, Union

import requests

from utilities.functions import stable_traceback
from utilities.type import ErrorMessage, Entities, Measurement, Responses, URL, Value


class SourceCollector(ABC):
    """Base class for source collectors. Source collectors are subclasses of this class that know how to collect the
    measurement data for one specific metric from one specific source."""

    TIMEOUT = 10  # Default timeout of 10 seconds
    MAX_ENTITIES = 100  # The maximum number of entities (e.g. violations, warnings) to send to the server
    source_type = ""  # The source type is set on the subclass, when the subclass is registered
    subclasses: Set[Type["SourceCollector"]] = set()

    def __init__(self, source, datamodel) -> None:
        self._datamodel = datamodel
        self.__parameters: Dict[str, Union[str, List[str]]] = source.get("parameters", {})

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
                matching_subclasses[0].source_type = source_type
                return matching_subclasses[0]
        raise LookupError(f"Couldn't find collector subclass for source {source_type} and metric {metric_type}")

    def get(self) -> Measurement:
        """Return the measurement from this source."""
        api_url = self._api_url()
        responses, connection_error = self.__safely_get_source_responses(api_url)
        value, total, entities, parse_error = self.__safely_parse_source_responses(responses)
        landing_url = self._landing_url(responses)
        return dict(api_url=api_url, landing_url=landing_url, value=value, total=total, entities=entities,
                    connection_error=connection_error, parse_error=parse_error)

    def _landing_url(self, responses: Responses) -> URL:  # pylint: disable=no-self-use,unused-argument
        """Return the user supplied landing url parameter if there is one, otherwise translate the url parameter into
        a default landing url."""
        landing_url = cast(str, self.__parameters.get("landing_url", "")).strip("/")
        if landing_url:
            return URL(landing_url)
        url = cast(str, self.__parameters.get("url", "")).strip("/")
        return URL(url[:-(len("xml"))] + "html" if url.endswith(".xml") else url)

    def _api_url(self) -> URL:  # pylint: disable=no-self-use
        """Translate the url parameter into the API url."""
        return URL(cast(str, self.__parameters.get("url", "")).strip("/"))

    def _parameter(self, parameter_key: str, quote: bool = False) -> Union[str, List[str]]:
        """Return the parameter value."""

        def quote_if_needed(parameter_value):
            """Quote the string if needed."""
            return urllib.parse.quote(parameter_value, safe="") if quote else parameter_value

        parameter_info = self._datamodel["sources"][self.source_type]["parameters"][parameter_key]
        if "values" in parameter_info:
            value = self.__parameters.get(parameter_key) or parameter_info["values"]
        else:
            default_value = parameter_info.get("default_value", "")
            value = self.__parameters.get(parameter_key, default_value)
        return quote_if_needed(value) if isinstance(value, str) else [quote_if_needed(item) for item in value]

    def __safely_get_source_responses(self, api_url: URL) -> Tuple[Responses, ErrorMessage]:
        """Connect to the source and get the data, without failing. This method should not be overridden
        because it makes sure the collection of source data never causes the collector to fail."""
        logging.info("Retrieving %s", api_url or self.__class__.__name__)
        responses: Responses = []
        error = None
        try:
            responses = self._get_source_responses(api_url)
            for response in responses:
                response.raise_for_status()
        except Exception:  # pylint: disable=broad-except
            error = stable_traceback(traceback.format_exc())
        return responses, error

    def _get_source_responses(self, api_url: URL) -> Responses:
        """Open the url. Can be overridden if a post request is needed or multiple requests need to be made."""
        return [requests.get(api_url, timeout=self.TIMEOUT, auth=self._basic_auth_credentials())]

    def _basic_auth_credentials(self) -> Optional[Tuple[str, str]]:
        """Return the basic authentication credentials, if any."""
        token = cast(str, self.__parameters.get("private_token", ""))
        if token:
            return token, ""
        username = cast(str, self.__parameters.get("username", ""))
        password = cast(str, self.__parameters.get("password", ""))
        return (username, password) if username and password else None

    def __safely_parse_source_responses(
            self, responses: Responses) -> Tuple[Value, Value, Entities, ErrorMessage]:
        """Parse the data from the responses, without failing. This method should not be overridden because it
        makes sure that the parsing of source data never causes the collector to fail."""
        entities: Entities = []
        value, total, error = None, None, None
        if responses:
            try:
                value = self._parse_source_responses_value(responses)
                total = self._parse_source_responses_total(responses)  # pylint: disable=assignment-from-none
                entities = self._parse_source_responses_entities(responses)
            except Exception:  # pylint: disable=broad-except
                error = stable_traceback(traceback.format_exc())
        return value, total, entities[:self.MAX_ENTITIES], error

    @abstractmethod
    def _parse_source_responses_value(self, responses: Responses) -> Value:
        # pylint: disable=no-self-use
        """Parse the responses to get the measurement for the metric. This method must be overridden by collectors
        to parse the retrieved sources data."""
        return None  # pragma: nocover

    def _parse_source_responses_total(self, responses: Responses) -> Value:
        # pylint: disable=no-self-use,unused-argument
        """Parse the responses to get the total for the metric. The total is the denominator for percentage
        scale metrics, i.e. measurement = (value / total) * 100%. This method can be overridden by collectors to
        parse the retrieved source data."""
        return "100"  # Return 100 by default so sources that already return a percentage simply work

    def _parse_source_responses_entities(self, responses: Responses) -> Entities:
        # pylint: disable=no-self-use,unused-argument
        """Parse the response to get the entities (e.g. violation, test cases, user stories) for the metric.
        This method can to be overridden by collectors when a source can provide the measured entities."""
        return []

    def next_collection(self) -> datetime:  # pylint: disable=no-self-use
        """Return when this source should be connected again for measurement data."""
        return datetime.now() + timedelta(seconds=15 * 60)


class LocalSourceCollector(SourceCollector, ABC):  # pylint: disable=abstract-method
    """Base class for source collectors that do not need to access the network but return static or user-supplied
    data."""

    def _get_source_responses(self, api_url: URL) -> Responses:
        return [requests.Response()]  # Return a fake response so that the parse methods will be called


class UnmergedBranchesSourceCollector(SourceCollector, ABC):  # pylint: disable=abstract-method
    """Base class for unmerged branches source collectors."""

    def _parse_source_responses_value(self, responses: Responses) -> Value:
        return str(len(self._unmerged_branches(responses)))

    def _parse_source_responses_entities(self, responses: Responses) -> Entities:
        return [
            dict(key=branch["name"], name=branch["name"], commit_age=str(self._commit_age(branch).days),
                 commit_date=str(self._commit_datetime(branch).date()))
            for branch in self._unmerged_branches(responses)]

    def _commit_age(self, branch) -> timedelta:
        """Return the age of the last commit on the branch."""
        return datetime.now(timezone.utc) - self._commit_datetime(branch)

    @abstractmethod
    def _unmerged_branches(self, responses: Responses) -> List:
        """Return the list of unmerged branch."""

    @abstractmethod
    def _commit_datetime(self, branch) -> datetime:
        """Return the date and time of the last commit on the branch."""
