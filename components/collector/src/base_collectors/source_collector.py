"""Source collector base classes."""

import asyncio
import traceback
from abc import ABC, abstractmethod
from collections.abc import Sequence
from datetime import datetime
from typing import ClassVar, TypedDict, cast

import aiohttp
from packaging.version import Version

from shared.utils.type import Direction
from shared_data_model import DATA_MODEL

from collector_utilities.date_time import days_ago, days_to_go
from collector_utilities.exceptions import CollectorError
from collector_utilities.functions import (
    match_string_or_regular_expression,
    stable_traceback,
    tokenless,
)
from collector_utilities.log import get_logger
from collector_utilities.type import URL, Response, Responses, Value
from model import Entities, Entity, IssueStatus, SourceMeasurement, SourceParameters, SourceResponses


class SourceCollector:
    """Base class for source collectors.

    Source collectors are subclasses of this class that know how to collect the
    measurement data for one specific metric from one specific source.
    """

    source_type = ""  # The source type is set on the subclass, when the subclass is registered
    subclasses: ClassVar[set[type["SourceCollector"]]] = set()

    def __init__(self, session: aiohttp.ClientSession, metric, source) -> None:
        self._session = session
        self._metric = metric
        self._issue_id = ""
        self.__parameters = SourceParameters(source)

    def __init_subclass__(cls) -> None:
        """Register the subclass as source collector."""
        SourceCollector.subclasses.add(cls)
        super().__init_subclass__()

    @classmethod
    def get_subclass(cls, source_type: str, metric_type: str) -> type["SourceCollector"] | None:
        """Return the subclass registered for the source/metric name.

        First try to find a match on both source type and metric type. If no match is found, return the generic
        collector for the source type.
        """
        for class_name in (f"{source_type}{metric_type}", source_type):
            for subclass in cls.subclasses:
                if subclass.__name__.lower() == class_name.replace("_", ""):
                    subclass.source_type = source_type
                    return subclass

        logger = get_logger()
        logger.warning("Couldn't find collector subclass for source %s and metric %s", source_type, metric_type)
        return None

    async def collect(self) -> SourceMeasurement:
        """Return the measurement from this source."""
        responses = await self.__safely_get_source_responses()
        measurement = await self.__safely_parse_source_responses(responses)
        measurement.api_url = responses.api_url
        measurement.landing_url = await self.__safely_parse_landing_url(responses)
        return measurement

    async def collect_issue_status(self, issue_id: str) -> IssueStatus:
        """Return the issue status from this source."""
        self._issue_id = issue_id
        responses = await self.__safely_get_source_responses()
        issue_status = await self.__safely_parse_issue_status(responses)
        issue_status.api_url = responses.api_url
        issue_status.landing_url = await self.__safely_parse_landing_url(responses)
        return issue_status

    async def _api_url(self) -> URL:
        """Translate the url parameter into the API url."""
        return self.__parameters.api_url()

    def _parameter(self, parameter_key: str, quote: bool = False) -> str | list[str]:
        """Return the parameter value."""
        return self.__parameters.get(parameter_key, quote)

    async def __safely_get_source_responses(self) -> SourceResponses:
        """Connect to the source and get the data, without failing.

        This method should not be overridden because it makes sure the collection of source data never causes the
        collector to fail.
        """
        logger = get_logger()
        api_url = safe_api_url = class_name = self.__class__.__name__
        try:
            api_url = await self._api_url()
            safe_api_url = tokenless(api_url) or class_name
            logger.info("%s retrieving %s", class_name, safe_api_url)
            responses = await asyncio.wait_for(self._get_source_responses(api_url), timeout=self._session.timeout.total)
            logger.info("%s retrieved %s", class_name, safe_api_url)
        except (TimeoutError, CollectorError, aiohttp.ClientError) as reason:
            error = self.__logsafe_exception(reason)
            logger.warning("%s failed to retrieve %s: %s", class_name, safe_api_url, error)
            responses = SourceResponses(api_url=URL(api_url), connection_error=error)
        except Exception as reason:
            error = stable_traceback(traceback.format_exc())
            reason_message = self.__logsafe_exception(reason)
            logger.error("%s failed to retrieve %s: %s", class_name, safe_api_url, reason_message)  # noqa: TRY400
            responses = SourceResponses(api_url=URL(api_url), connection_error=error)
        return responses

    @staticmethod
    def __logsafe_exception(exception: Exception) -> str:
        """Return a log-safe version of the exception."""
        return tokenless(str(exception)) if str(exception) else exception.__class__.__name__

    async def _get_source_responses(self, *urls: URL) -> SourceResponses:
        """Open the url(s). Can be overridden if a post request is needed or serial requests need to be made."""
        auth = aiohttp.BasicAuth(*credentials) if (credentials := self._basic_auth_credentials()) else None
        headers = self._headers()
        tasks = [self._session.get(url, allow_redirects=True, headers=headers, auth=auth) for url in urls if url]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        for response in responses:
            if isinstance(response, Exception):
                raise response
        return SourceResponses(responses=cast(Responses, responses), api_url=urls[0])

    def _basic_auth_credentials(self) -> tuple[str, str] | None:
        """Return the basic authentication credentials, if any."""
        if token := self.__parameters.private_token():
            return token, ""
        credentials = username, password = self.__parameters.username(), self.__parameters.password()
        return credentials if username and password else None

    def _headers(self) -> dict[str, str]:
        """Return the headers for the get request."""
        return {}

    async def __safely_parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Parse the data from the responses, without failing.

        This method should not be overridden because it makes sure that the parsing of source data never causes the
        collector to fail.
        """
        if responses.connection_error:
            return SourceMeasurement(connection_error=responses.connection_error)
        try:
            return await self._parse_source_responses(responses)
        except CollectorError as reason:
            error = self.__logsafe_exception(reason)
            return SourceMeasurement(parse_error=error)
        except Exception:
            return SourceMeasurement(parse_error=stable_traceback(traceback.format_exc()))

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Parse the responses to get the measurement value, the total value, and the entities for the metric.

        Either this method or self._parse_entities() need to be overridden in the subclass to implement the actual
        parsing of the source responses.
        """
        entities = await self._parse_entities(responses)
        included_entities = Entities([entity for entity in entities if self._include_entity(entity)])
        return SourceMeasurement(
            entities=included_entities,
            total=await self._parse_total(responses, entities),
            value=await self._parse_value(responses, included_entities),
        )

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Parse the entities from the responses."""
        return Entities()

    def _include_entity(self, entity: Entity) -> bool:
        """Return whether to include the entity in the measurement."""
        return True

    async def _parse_value(self, responses: SourceResponses, included_entities: Entities) -> Value:
        """Parse the value from the responses."""
        return str(len(included_entities))

    async def _parse_total(self, responses: SourceResponses, entities: Entities) -> Value:
        """Parse the total from the responses."""
        return str(len(entities))

    async def __safely_parse_issue_status(self, responses: SourceResponses) -> IssueStatus:
        """Parse the issue status from the source responses, without failing.

        This method should not be overridden because it makes sure that the parsing of source data never causes the
        collector to fail.
        """
        if responses.connection_error:
            return IssueStatus(self._issue_id, connection_error=responses.connection_error)
        try:
            return await self._parse_issue_status(responses)
        except Exception:
            return IssueStatus(self._issue_id, parse_error=stable_traceback(traceback.format_exc()))

    async def _parse_issue_status(self, responses: SourceResponses) -> IssueStatus:
        """Parse the responses to get the status of the metric's linked issue."""
        return IssueStatus(self._issue_id)  # pragma: no cover

    async def __safely_parse_landing_url(self, responses: SourceResponses) -> URL:
        """Parse the responses to get the landing url, without failing.

        This method should not be overridden because it makes sure that the parsing of source data never causes the
        collector to fail.
        """
        try:
            return await self._landing_url(responses)
        except Exception:
            return await self._api_url()

    async def _landing_url(self, responses: SourceResponses) -> URL:
        """Return a user-friendly landing url.

        Return the user supplied landing url parameter if there is one, otherwise return the API URL.
        """
        return self.__parameters.landing_url() or self.__parameters.api_url()

    @property
    def metric_direction(self) -> Direction:
        """Return the metric direction."""
        return cast(
            Direction,
            str(self._metric.get("direction") or DATA_MODEL.metrics[self._metric["type"]].direction.value),
        )


class BranchType(TypedDict):
    """Branch."""

    name: str


class InactiveBranchesSourceCollector[Branch: BranchType](SourceCollector, ABC):
    """Base class for inactive branches source collectors."""

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Override to get the inactive branches from the inactive branches method that subclasses should implement."""
        return Entities(
            Entity(
                key=branch["name"],
                name=branch["name"],
                commit_date=str(self._commit_datetime(branch).date()),
                merge_status="merged" if self._is_branch_merged(branch) else "unmerged",
                url=str(self._branch_landing_url(branch)),
            )
            for branch in await self._inactive_branches(responses)
        )

    async def _inactive_branches(self, responses: SourceResponses) -> list[Branch]:
        """Return the list of inactive branches."""
        return [
            branch
            for branch in await self._branches(responses)
            if not self._is_default_branch(branch)
            and self._has_allowed_merge_status(branch)
            and self._is_branch_inactive(branch)
            and not self._ignore_branch(branch)
        ]

    @abstractmethod
    async def _branches(self, responses: SourceResponses) -> list[Branch]:
        """Return a list of branches from the responses."""

    @abstractmethod
    def _is_default_branch(self, branch: Branch) -> bool:
        """Return whether the branch is the default branch."""

    def _has_allowed_merge_status(self, branch: Branch) -> bool:
        """Return whether the branch has the configured status."""
        allowed_statuses = self._parameter("branch_merge_status")
        if self._is_branch_merged(branch):
            return "merged" in allowed_statuses
        return "unmerged" in allowed_statuses

    @abstractmethod
    def _is_branch_merged(self, branch: Branch) -> bool:
        """Return whether the branch has been merged with the default branch."""

    def _is_branch_inactive(self, branch: Branch) -> bool:
        """Return whether the branch has not recently been committed to."""
        return days_ago(self._commit_datetime(branch)) > int(cast(str, self._parameter("inactive_days")))

    def _ignore_branch(self, branch: Branch) -> bool:
        """Return whether to ignore the branch."""
        return match_string_or_regular_expression(branch["name"], self._parameter("branches_to_ignore"))

    @abstractmethod
    def _commit_datetime(self, branch: Branch) -> datetime:
        """Return the date and time of the last commit on the branch."""

    @abstractmethod
    def _branch_landing_url(self, branch: Branch) -> URL:
        """Return the landing url of the branch."""


class SecurityWarningsSourceCollector(SourceCollector):
    """Base class for security warnings source collectors."""

    SEVERITY_PARAMETER = "severities"
    ENTITY_SEVERITY_ATTRIBUTE = "severity"
    MAKE_ENTITY_SEVERITY_VALUE_LOWER_CASE = False

    FIX_AVAILABILITY_PARAMETER = "fix_availability"
    ENTITY_FIX_AVAILABILITY_ATTRIBUTE = "fix"

    def _include_entity(self, entity: Entity) -> bool:
        """Return whether to include the security warning in the measurement."""
        severity = str(entity[self.ENTITY_SEVERITY_ATTRIBUTE])
        if self.MAKE_ENTITY_SEVERITY_VALUE_LOWER_CASE:
            severity = severity.lower()
        if severity not in self._parameter(self.SEVERITY_PARAMETER):
            return False
        if self.FIX_AVAILABILITY_PARAMETER in DATA_MODEL.sources[self.source_type].parameters:
            fix_availability = self._parameter(self.FIX_AVAILABILITY_PARAMETER)
            fix = entity[self.ENTITY_FIX_AVAILABILITY_ATTRIBUTE]
            fix_available = fix and fix not in ("None", "0")
            entity_should_have_fix_but_does_not = fix_availability == ["fix available"] and not fix_available
            entity_should_not_have_fix_but_does = fix_availability == ["no fix available"] and fix_available
            if entity_should_have_fix_but_does_not or entity_should_not_have_fix_but_does:
                return False
        return super()._include_entity(entity)


class TimeCollector(SourceCollector):
    """Base class for time collectors."""

    async def _parse_value(self, responses: SourceResponses, included_entities: Entities) -> Value:
        """Parse the value from the responses."""
        date_times = await self._parse_source_response_date_times(responses)
        return str(self.days(self.minimum(date_times)))

    async def _parse_source_response_date_times(self, responses: SourceResponses) -> Sequence[datetime]:
        """Parse the source update datetimes from the responses and return the datetimes."""
        return await asyncio.gather(*[self._parse_source_response_date_time(response) for response in responses])

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        """Parse the datetime from the source."""
        raise NotImplementedError  # pragma: no cover

    @staticmethod
    def days(date_time: datetime) -> int:
        """Return the time between the current date time and the specified date time."""
        raise NotImplementedError  # pragma: no cover

    def minimum(self, date_times: Sequence[datetime]) -> datetime:
        """Allow for overriding what the minimum of the datetimes is: the newest or the oldest."""
        return min(date_times) if self.metric_direction == "<" else max(date_times)


class TimePassedCollector(TimeCollector):
    """Base class for source up-to-dateness collectors."""

    @staticmethod
    def days(date_time: datetime) -> int:
        """Override to return the number of days since the date time."""
        return days_ago(date_time)


class TimeRemainingCollector(TimeCollector):
    """Base class for time remaining collectors."""

    @staticmethod
    def days(date_time: datetime) -> int:
        """Override to return the number of days until the date time."""
        return days_to_go(date_time)


class VersionCollector(SourceCollector):
    """Base class for version collectors."""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to get the version from the parse version method that subclasses should implement."""
        versions = await self._parse_source_response_versions(responses)
        return SourceMeasurement(value=str(min(versions)))

    async def _parse_source_response_versions(self, responses: SourceResponses) -> Sequence[Version]:
        """Parse the source versions from the responses and return the versions."""
        return await asyncio.gather(*[self._parse_source_response_version(response) for response in responses])

    async def _parse_source_response_version(self, response: Response) -> Version:
        """Parse the version from the source response."""
        raise NotImplementedError  # pragma: no cover


class TransactionEntity(Entity):
    """Entity representing a performance transaction."""

    def is_to_be_included(self, transactions_to_include: list[str], transactions_to_ignore: list[str]) -> bool:
        """Return whether the transaction should be included."""
        name = self["name"]
        if transactions_to_include and not match_string_or_regular_expression(name, transactions_to_include):
            return False
        return not match_string_or_regular_expression(name, transactions_to_ignore)

    def is_slow(
        self,
        response_time_to_evaluate: str,
        target_response_time: float,
        transaction_specific_target_response_times: list[str],
    ) -> bool:
        """Return whether the transaction is slow."""
        name, response_time = self["name"], float(self[response_time_to_evaluate])
        for transaction_specific_target_response_time in transaction_specific_target_response_times:
            re_or_name, target = transaction_specific_target_response_time.rsplit(":", maxsplit=1)
            if match_string_or_regular_expression(name, [re_or_name]):
                return response_time > float(target)
        return bool(response_time > target_response_time)


class SlowTransactionsCollector(SourceCollector):
    """Base class for slow transactions collectors."""

    def __init__(self, session: aiohttp.ClientSession, metric, source) -> None:
        """Extend to set up the parameters."""
        super().__init__(session, metric, source)
        self.__transactions_to_include = cast(list[str], self._parameter("transactions_to_include"))
        self.__transactions_to_ignore = cast(list[str], self._parameter("transactions_to_ignore"))
        self._response_time_to_evaluate = cast(str, self._parameter("response_time_to_evaluate"))
        self.__target_response_time = float(cast(int, self._parameter("target_response_time")))
        self.__transaction_specific_target_response_times = cast(
            list[str],
            self._parameter("transaction_specific_target_response_times"),
        )

    def _is_to_be_included_and_is_slow(self, entity: TransactionEntity) -> bool:
        """Return whether the transaction entity is to be included and is slow."""
        return entity.is_to_be_included(
            self.__transactions_to_include,
            self.__transactions_to_ignore,
        ) and entity.is_slow(
            self._response_time_to_evaluate,
            self.__target_response_time,
            self.__transaction_specific_target_response_times,
        )

    @staticmethod
    def _round(value: float) -> str:
        """Round the value at exactly one decimal."""
        return str(round(float(value), 1))


class MergeRequestCollector(SourceCollector):
    """Base class for merge request collectors."""

    def _include_entity(self, entity: Entity) -> bool:
        """Return whether the merge request should be counted."""
        return (
            self._request_matches_branches(entity)
            and self._request_matches_approval(entity)
            and self._request_matches_state(entity)
            and self._request_matches_upvotes(entity)
        )

    def _request_matches_approval(self, entity: Entity) -> bool:
        """Return whether the merge request approval matches the configured approval."""
        return True

    def _request_matches_branches(self, entity: Entity) -> bool:
        """Return whether the merge request target branch matches the configured branches."""
        branches = self._parameter("target_branches_to_include")
        target_branch = entity["target_branch"]
        return match_string_or_regular_expression(target_branch, branches) if branches else True

    def _request_matches_state(self, entity: Entity) -> bool:
        """Return whether the merge request state matches the configured states."""
        return entity["state"] in self._parameter("merge_request_state")

    def _request_matches_upvotes(self, entity: Entity) -> bool:
        """Return whether the merge request upvotes matches the configured upvotes."""
        # If the required number of upvotes is zero, merge requests are included regardless of how many upvotes they
        # actually have. If the required number of upvotes is more than zero then only merge requests that have fewer
        # than the minimum number of upvotes are included in the count:
        required_upvotes = int(cast(str, self._parameter("upvotes")))
        return required_upvotes == 0 or int(entity["upvotes"]) < required_upvotes
