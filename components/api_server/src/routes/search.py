"""Search endpoint."""

from typing import Literal, TypedDict, TYPE_CHECKING

import bottle

from database.reports import latest_reports
from model.iterators import metrics, sources, subjects
from utils.log import get_logger

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence

    from pymongo.database import Database

    from shared.utils.type import ItemId

    from model.report import Report


DomainObjectType = Literal["metric", "report", "source", "subject"]
SearchQuery = dict[str, str]

# Base types for the search endpoint responses:


class BaseSearchResponse(TypedDict):
    """Base class for search responses."""

    domain_object_type: DomainObjectType


class BaseQueryParsedSearchResponse(BaseSearchResponse):
    """Base class for responses after successfully parsing the search query."""

    search_query: SearchQuery


class BaseFailedSearchResponse(BaseSearchResponse):
    """Base class for responses after failed searches."""

    error: str
    ok: Literal[False]  # Would be nice to set False as default value as well, but that's not possible with TypedDict.


# Concrete types for the search endpoint responses:


class SearchResults(BaseQueryParsedSearchResponse):
    """Response for successful searches."""

    ok: Literal[True]  # Would be nice to set True as default value as well, but that's not possible with TypedDict.
    uuids: Sequence[ItemId]


class ParseError(BaseFailedSearchResponse):
    """Response for failed search query parsing."""


class SearchError(BaseQueryParsedSearchResponse, BaseFailedSearchResponse):  # type: ignore[misc]
    """Response for searches that failed after successfully parsing the search query."""

    # Ignore the false positive mypy error: Overwriting TypedDict field "domain_object_type" while merging.
    # See https://github.com/python/mypy/issues/8714.


def match_attribute(
    domain_object_type: DomainObjectType, domain_object, attribute_name: str, attribute_value: str
) -> bool:
    """Return whether the domain object has an attribute with the specified name and value."""
    # Note that we don't use domain_object.get(attribute_name) because that would make it impossible to search for None.
    if domain_object_type == "source":
        parameters = domain_object["parameters"]
        if attribute_name in parameters and parameters[attribute_name] == attribute_value:
            return True
    return attribute_name in domain_object and domain_object[attribute_name] == attribute_value


@bottle.post("/api/v3/<domain_object_type>/search", authentication_required=False)
def search(domain_object_type: DomainObjectType, database: Database) -> SearchResults | ParseError | SearchError:
    """Search for domain objects of the specified type by attribute value."""
    logger = get_logger()
    try:
        query = dict(bottle.request.json)
        attribute_name, attribute_value = set(query.items()).pop()
    except Exception as reason:  # noqa: BLE001
        logger.warning("Parsing search query for %s failed: %s", domain_object_type, reason)
        return ParseError(domain_object_type=domain_object_type, error=str(reason), ok=False)
    try:
        reports = latest_reports(database)
        if domain_object_type == "report":
            domain_objects: list[Report] | Iterator[Report] = reports
        else:
            domain_objects = {"metric": metrics, "source": sources, "subject": subjects}[domain_object_type](*reports)
        uuids = [
            domain_object.uuid
            for domain_object in domain_objects
            if match_attribute(domain_object_type, domain_object, attribute_name, attribute_value)
        ]
    except Exception as reason:  # pragma: no feature-test-cover # noqa: BLE001
        logger.warning("Searching for %s failed: %s", domain_object_type, reason)
        return SearchError(domain_object_type=domain_object_type, error=str(reason), ok=False, search_query=query)
    return SearchResults(domain_object_type=domain_object_type, ok=True, search_query=query, uuids=uuids)
