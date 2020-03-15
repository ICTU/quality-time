"""Source collector base classes."""

import asyncio
import json
import logging
import traceback
import urllib
from abc import ABC, abstractmethod
from datetime import datetime
from http import HTTPStatus
from typing import cast, Any, Dict, Final, List, Optional, Set, Tuple, Type, Union

import aiohttp

from collector_utilities.functions import days_ago, tokenless, stable_traceback
from collector_utilities.type import ErrorMessage, Entities, JSON, Measurement, Response, Responses, URL, Value


class SourceCollector(ABC):
    """Base class for source collectors. Source collectors are subclasses of this class that know how to collect the
    measurement data for one specific metric from one specific source."""

    MAX_ENTITIES = 100  # The maximum number of entities (e.g. violations, warnings) to send to the server
    API_URL_PARAMETER_KEY = "url"
    source_type = ""  # The source type is set on the subclass, when the subclass is registered
    subclasses: Set[Type["SourceCollector"]] = set()

    def __init__(self, session: aiohttp.ClientSession, source, datamodel) -> None:
        self._session = session
        self._datamodel: Final = datamodel
        self.__parameters: Final[Dict[str, Union[str, List[str]]]] = source.get("parameters", {})

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

    async def get(self) -> Measurement:
        """Return the measurement from this source."""
        responses, api_url, connection_error = await self.__safely_get_source_responses()
        value, total, entities, parse_error = await self.__safely_parse_source_responses(responses)
        landing_url = await self.__safely_parse_landing_url(responses)
        return dict(api_url=api_url, landing_url=landing_url, value=value, total=total, entities=entities,
                    connection_error=connection_error, parse_error=parse_error)

    async def _api_url(self) -> URL:
        """Translate the url parameter into the API url."""
        return URL(cast(str, self.__parameters.get(self.API_URL_PARAMETER_KEY, "")).rstrip("/"))

    def _parameter(self, parameter_key: str, quote: bool = False) -> Union[str, List[str]]:
        """Return the parameter value."""

        def quote_if_needed(parameter_value: str) -> str:
            """Quote the string if needed."""
            return urllib.parse.quote(parameter_value, safe="") if quote else parameter_value

        parameter_info = self._datamodel["sources"][self.source_type]["parameters"][parameter_key]
        if "values" in parameter_info and parameter_info["type"].startswith("multiple_choice"):
            value = self.__parameters.get(parameter_key) or parameter_info["values"]
        else:
            default_value = parameter_info.get("default_value", "")
            value = self.__parameters.get(parameter_key, default_value)
        if api_values := parameter_info.get("api_values"):
            value = api_values.get(value, value) if isinstance(value, str) else [api_values.get(v, v) for v in value]
        if parameter_key.endswith("url"):
            value = cast(str, value).rstrip("/")
        return quote_if_needed(value) if isinstance(value, str) else [quote_if_needed(v) for v in value]

    async def __safely_get_source_responses(self) -> Tuple[Responses, URL, ErrorMessage]:
        """Connect to the source and get the data, without failing. This method should not be overridden
        because it makes sure the collection of source data never causes the collector to fail."""
        responses: Responses = []
        api_url = URL("")
        error = None
        try:
            responses = await self._get_source_responses(api_url := await self._api_url())
            logging.info("Retrieved %s", tokenless(api_url) or self.__class__.__name__)
        except Exception as reason:  # pylint: disable=broad-except
            error = stable_traceback(traceback.format_exc())
            logging.warning("Failed to retrieve %s: %s", tokenless(api_url) or self.__class__.__name__, reason)
        return responses, api_url, error

    async def _get_source_responses(self, *urls: URL) -> Responses:
        """Open the url. Can be overridden if a post request is needed or serial requests need to be made."""
        kwargs: Dict[str, Any] = dict()
        credentials = self._basic_auth_credentials()
        if credentials is not None:
            kwargs["auth"] = aiohttp.BasicAuth(credentials[0], credentials[1])
        if headers := self._headers():
            kwargs["headers"] = headers
        tasks = [self._session.get(url, **kwargs) for url in urls]
        return list(await asyncio.gather(*tasks))

    def _basic_auth_credentials(self) -> Optional[Tuple[str, str]]:
        """Return the basic authentication credentials, if any."""
        if token := cast(str, self.__parameters.get("private_token", "")):
            return token, ""
        username = cast(str, self.__parameters.get("username", ""))
        password = cast(str, self.__parameters.get("password", ""))
        return (username, password) if username and password else None

    def _headers(self) -> Dict[str, str]:  # pylint: disable=no-self-use
        """Return the headers for the get request."""
        return {}

    async def __safely_parse_source_responses(
            self, responses: Responses) -> Tuple[Value, Value, Entities, ErrorMessage]:
        """Parse the data from the responses, without failing. This method should not be overridden because it
        makes sure that the parsing of source data never causes the collector to fail."""
        entities: Entities = []
        value, total, error = None, None, None
        if responses:
            try:
                value, total, entities = await self._parse_source_responses(responses)
            except Exception:  # pylint: disable=broad-except
                error = stable_traceback(traceback.format_exc())
        return value, total, entities[:self.MAX_ENTITIES], error

    async def _parse_source_responses(self, responses: Responses) -> Tuple[Value, Value, Entities]:
        """Parse the responses to get the measurement value, the total value, and the entities for the metric.
        This method can be overridden by collectors to parse the retrieved sources data."""
        # pylint: disable=assignment-from-none,no-self-use,unused-argument
        return None, "100", []  # pragma nocover

    async def __safely_parse_landing_url(self, responses: Responses) -> URL:
        """Parse the responses to get the landing url, without failing. This method should not be overridden because
        it makes sure that the parsing of source data never causes the collector to fail."""
        try:
            return await self._landing_url(responses)
        except Exception:  # pylint: disable=broad-except
            return await self._api_url()

    async def _landing_url(self, responses: Responses) -> URL:  # pylint: disable=unused-argument
        """Return the user supplied landing url parameter if there is one, otherwise translate the url parameter into
        a default landing url."""
        if landing_url := cast(str, self.__parameters.get("landing_url", "")).rstrip("/"):
            return URL(landing_url)
        url = cast(str, self.__parameters.get(self.API_URL_PARAMETER_KEY, "")).rstrip("/")
        return URL(url[:-(len("xml"))] + "html" if url.endswith(".xml") else url)


class FakeResponse:  # pylint: disable=too-few-public-methods
    """Fake a response because aiohttp.ClientResponse can not easily be instantiated directly. """
    status = HTTPStatus.OK

    def __init__(self, contents: bytes = bytes()) -> None:
        super().__init__()
        self.contents = contents

    async def json(self) -> JSON:
        """Return the JSON version of the contents."""
        return cast(JSON, json.loads(self.contents))

    async def text(self) -> str:
        """Return the text version of the contents."""
        return str(self.contents.decode())


class LocalSourceCollector(SourceCollector, ABC):  # pylint: disable=abstract-method
    """Base class for source collectors that do not need to access the network but return static or user-supplied
    data."""

    async def _get_source_responses(self, *urls: URL) -> Responses:
        return [cast(Response, FakeResponse())]  # Return a fake response so that the parse methods will be called


class UnmergedBranchesSourceCollector(SourceCollector, ABC):  # pylint: disable=abstract-method
    """Base class for unmerged branches source collectors."""

    async def _parse_source_responses(self, responses: Responses) -> Tuple[Value, Value, Entities]:
        entities = [
            dict(key=branch["name"], name=branch["name"], commit_age=str(days_ago(self._commit_datetime(branch))),
                 commit_date=str(self._commit_datetime(branch).date()))
            for branch in await self._unmerged_branches(responses)]
        return str(len(entities)), "100", entities

    @abstractmethod
    async def _unmerged_branches(self, responses: Responses) -> List[Dict[str, Any]]:
        """Return the list of unmerged branches."""

    @abstractmethod
    def _commit_datetime(self, branch) -> datetime:
        """Return the date and time of the last commit on the branch."""


class SourceUpToDatenessCollector(SourceCollector):
    """Base class for source up-to-dateness collectors."""

    async def _parse_source_responses(self, responses: Responses) -> Tuple[Value, Value, Entities]:
        date_times = await asyncio.gather(*[self._parse_source_response_date_time(response) for response in responses])
        return str(days_ago(min(date_times))), "100", []

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        """Parse the date time from the source."""
        raise NotImplementedError  # pragma: nocover
