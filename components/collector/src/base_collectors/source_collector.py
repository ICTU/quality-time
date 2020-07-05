"""Source collector base classes."""

import asyncio
import logging
import traceback
import urllib
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Final, List, Optional, Set, Sequence, Tuple, Type, Union, cast

import aiohttp

from collector_utilities.functions import days_ago, stable_traceback, tokenless
from collector_utilities.type import URL, Response
from source_model import Entity, SourceMeasurement, SourceResponses


class SourceCollector(ABC):
    """Base class for source collectors. Source collectors are subclasses of this class that know how to collect the
    measurement data for one specific metric from one specific source."""

    API_URL_PARAMETER_KEY = "url"
    source_type = ""  # The source type is set on the subclass, when the subclass is registered
    subclasses: Set[Type["SourceCollector"]] = set()

    def __init__(self, session: aiohttp.ClientSession, source, data_model) -> None:
        self._session = session
        self._data_model: Final = data_model
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

    async def get(self):
        """Return the measurement from this source."""
        responses = await self.__safely_get_source_responses()
        measurement = await self.__safely_parse_source_responses(responses)
        landing_url = await self.__safely_parse_landing_url(responses)
        return dict(
            api_url=responses.api_url, landing_url=landing_url, value=measurement.value, total=measurement.total,
            entities=measurement.entities, connection_error=responses.connection_error,
            parse_error=measurement.parse_error)

    async def _api_url(self) -> URL:
        """Translate the url parameter into the API url."""
        return URL(cast(str, self.__parameters.get(self.API_URL_PARAMETER_KEY, "")).rstrip("/"))

    def _parameter(self, parameter_key: str, quote: bool = False) -> Union[str, List[str]]:
        """Return the parameter value."""

        def quote_if_needed(parameter_value: str) -> str:
            """Quote the string if needed."""
            return urllib.parse.quote(parameter_value, safe="") if quote else parameter_value

        parameter_info = self._data_model["sources"][self.source_type]["parameters"][parameter_key]
        if "values" in parameter_info and parameter_info["type"].startswith("multiple_choice"):
            value = self.__parameters.get(parameter_key) or parameter_info["values"]
            if parameter_info["type"] == "multiple_choice":
                # Ensure all values picked by the user are still allowed. Remove any values that are no longer allowed:
                value = [v for v in value if v in parameter_info["values"]] or parameter_info["values"]
        else:
            default_value = parameter_info.get("default_value", "")
            value = self.__parameters.get(parameter_key) or default_value
        if api_values := parameter_info.get("api_values"):
            value = api_values.get(value, value) if isinstance(value, str) else [api_values.get(v, v) for v in value]
        if parameter_key.endswith("url"):
            value = cast(str, value).rstrip("/")
        return quote_if_needed(value) if isinstance(value, str) else [quote_if_needed(v) for v in value]

    async def __safely_get_source_responses(self) -> SourceResponses:
        """Connect to the source and get the data, without failing. This method should not be overridden
        because it makes sure the collection of source data never causes the collector to fail."""
        api_url = safe_api_url = self.__class__.__name__
        try:
            api_url = await self._api_url()
            safe_api_url = tokenless(api_url) or self.__class__.__name__
            responses = await self._get_source_responses(api_url)
            logging.info("Retrieved %s", safe_api_url)
            return responses
        except aiohttp.ClientError as reason:
            error = tokenless(str(reason)) if str(reason) else reason.__class__.__name__
            logging.warning("Failed to retrieve %s: %s", safe_api_url, error)
        except Exception as reason:  # pylint: disable=broad-except
            error = stable_traceback(traceback.format_exc())
            logging.error("Failed to retrieve %s: %s", safe_api_url, reason)
        return SourceResponses(api_url=URL(api_url), connection_error=error)

    async def _get_source_responses(self, *urls: URL) -> SourceResponses:
        """Open the url(s). Can be overridden if a post request is needed or serial requests need to be made."""
        kwargs: Dict[str, Any] = {}
        credentials = self._basic_auth_credentials()
        if credentials is not None:
            kwargs["auth"] = aiohttp.BasicAuth(credentials[0], credentials[1])
        if headers := self._headers():
            kwargs["headers"] = headers
        tasks = [self._session.get(url, **kwargs) for url in urls if url]
        return SourceResponses(responses=list(await asyncio.gather(*tasks)), api_url=urls[0])

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

    async def __safely_parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Parse the data from the responses, without failing. This method should not be overridden because it
        makes sure that the parsing of source data never causes the collector to fail."""
        if responses.connection_error:
            measurement = SourceMeasurement(total=None)
        else:
            try:
                measurement = await self._parse_source_responses(responses)
            except Exception:  # pylint: disable=broad-except
                measurement = SourceMeasurement(parse_error=stable_traceback(traceback.format_exc()))
        return measurement

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Parse the responses to get the measurement value, the total value, and the entities for the metric.
        This method should be overridden by collectors to parse the retrieved sources data."""
        # pylint: disable=no-self-use,unused-argument
        raise NotImplementedError

    async def __safely_parse_landing_url(self, responses: SourceResponses) -> URL:
        """Parse the responses to get the landing url, without failing. This method should not be overridden because
        it makes sure that the parsing of source data never causes the collector to fail."""
        try:
            return await self._landing_url(responses)
        except Exception:  # pylint: disable=broad-except
            return await self._api_url()

    async def _landing_url(self, responses: SourceResponses) -> URL:  # pylint: disable=unused-argument
        """Return the user supplied landing url parameter if there is one, otherwise translate the url parameter into
        a default landing url."""
        if landing_url := cast(str, self.__parameters.get("landing_url", "")).rstrip("/"):
            return URL(landing_url)
        url = cast(str, self.__parameters.get(self.API_URL_PARAMETER_KEY, "")).rstrip("/")
        return URL(url.removesuffix("xml") + "html" if url.endswith(".xml") else url)


class UnmergedBranchesSourceCollector(SourceCollector, ABC):  # pylint: disable=abstract-method
    """Base class for unmerged branches source collectors."""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        entities = [
            Entity(
                key=branch["name"], name=branch["name"], commit_date=str(self._commit_datetime(branch).date()),
                url=str(self._branch_landing_url(branch)))
            for branch in await self._unmerged_branches(responses)]
        return SourceMeasurement(entities=entities)

    @abstractmethod
    async def _unmerged_branches(self, responses: SourceResponses) -> List[Dict[str, Any]]:
        """Return the list of unmerged branches."""

    @abstractmethod
    def _commit_datetime(self, branch) -> datetime:
        """Return the date and time of the last commit on the branch."""

    @abstractmethod
    def _branch_landing_url(self, branch) -> URL:
        """Return the landing url of the branch."""


class SourceUpToDatenessCollector(SourceCollector):
    """Base class for source up-to-dateness collectors."""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        date_times = await self._parse_source_response_date_times(responses)
        return SourceMeasurement(value=str(days_ago(min(date_times))))

    async def _parse_source_response_date_times(self, responses: SourceResponses) -> Sequence[datetime]:
        return await asyncio.gather(*[self._parse_source_response_date_time(response) for response in responses])

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        """Parse the date time from the source."""
        raise NotImplementedError  # pragma: no cover
