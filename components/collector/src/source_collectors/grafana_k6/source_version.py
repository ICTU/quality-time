"""Grafana k6 source version collector."""

from typing import TYPE_CHECKING, cast

from packaging.version import Version

from base_collectors import JSONFileSourceCollector, VersionCollector
from collector_utilities.exceptions import CollectorError

from .json_types import SummaryJSON

if TYPE_CHECKING:
    from collector_utilities.type import Response


class GrafanaK6SourceVersion(JSONFileSourceCollector, VersionCollector):
    """Collector to collect the Grafana k6 version."""

    async def _parse_source_response_version(self, response: Response) -> Version:
        """Parse the version from the source response."""
        json = cast(SummaryJSON, await response.json(content_type=None))
        try:
            # k6 v1.7.x uses "k6_version" instead of "k6Version" as specified by the schema, so support both.
            metadata = json["metadata"]
            return Version(metadata.get("k6Version") or metadata["k6_version"])
        except KeyError as error:
            message = 'Could not find an object {"metadata": {"k6Version": value}} in summary.json.'
            raise CollectorError(message) from error
