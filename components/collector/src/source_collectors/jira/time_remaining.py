"""Jira time remaining collector."""

from typing import TYPE_CHECKING
from urllib.parse import urlsplit

from base_collectors.source_collector import TimeRemainingCollector
from collector_utilities.date_time import parse_datetime
from collector_utilities.type import URL, Response

from .base import JiraBoardBase

if TYPE_CHECKING:
    from datetime import datetime

    from model import SourceResponses


class JiraTimeRemaining(JiraBoardBase, TimeRemainingCollector):
    """Collector to get the time remaining until end of the active sprint from Jira."""

    async def _get_source_responses(self, *urls: URL) -> SourceResponses:
        """Extend to pass the sprint API."""
        board_id = await self._board_id(urls[0])
        api_url = URL(f"{urls[0]}/rest/agile/1.0/board/{board_id}/sprint?state=active")
        return await super()._get_source_responses(api_url)

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        """Parse the datetime from the source."""
        sprints = await response.json()
        # Assume there is one active sprint:
        return parse_datetime(sprints["values"][0]["endDate"])

    async def _landing_url(self, responses: SourceResponses) -> URL:
        """Override to return the URL for the active sprint."""
        sprints = await responses[0].json()
        sprint = sprints["values"][0]
        splitted_self_url = urlsplit(str(sprint["self"]))
        api_url = f"{splitted_self_url.scheme}://{splitted_self_url.netloc}"
        return URL(
            f"{api_url}/secure/RapidBoard.jspa?rapidView={sprint['originBoardId']}&view=reporting&"
            f"chart=sprintRetrospective&sprint={sprint['id']}#"
        )
