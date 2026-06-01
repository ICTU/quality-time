"""Utilities for collecting data from GraphQL APIs."""

from typing import TYPE_CHECKING

from model import SourceResponses

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    import aiohttp

# A GraphQL page fetcher takes a cursor and returns the page response, whether there is a next page, and the
# cursor to the next page:
type GraphQLPageFetcher = Callable[[str], Awaitable[tuple[aiohttp.ClientResponse, bool, str]]]


async def collect_graphql_responses(get_page: GraphQLPageFetcher) -> SourceResponses:
    """Return the responses for all pages, following the GraphQL cursor-based pagination."""
    responses, has_next_page, cursor = SourceResponses(), True, ""
    while has_next_page:
        response, has_next_page, cursor = await get_page(cursor)
        responses.append(response)
    return responses
