"""Grafana k6 source up-to-dateness collector."""

from typing import TYPE_CHECKING, cast

from base_collectors import JSONFileSourceCollector, TimePassedCollector
from collector_utilities.date_time import parse_datetime
from collector_utilities.exceptions import CollectorError

from .json_types import SummaryJSON

if TYPE_CHECKING:
    from datetime import datetime

    from collector_utilities.type import Response


class GrafanaK6SourceUpToDateness(JSONFileSourceCollector, TimePassedCollector):
    """Grafana k6 collector for source up-to-dateness."""

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        """Override to parse the date of the report."""
        json = cast(SummaryJSON, await response.json(content_type=None))
        try:
            return parse_datetime(json["metadata"]["generatedAt"])
        except KeyError as error:
            message = 'Could not find an object {"metadata": {"generatedAt": value}} in summary.json.'
            raise CollectorError(message) from error
