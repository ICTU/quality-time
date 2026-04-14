"""Metric collector that returns a manually entered version."""

from typing import TYPE_CHECKING

from packaging.version import Version

from base_collectors import SourceCollector

if TYPE_CHECKING:
    from collector_utilities.type import Value
    from model import Entities, SourceResponses


class ManualVersion(SourceCollector):
    """Manual version collector."""

    async def _parse_value(self, responses: SourceResponses, included_entities: Entities) -> Value:
        """Override to return the user-supplied manual version."""
        return str(Version(str(self._parameter("version"))))  # Check whether the version is valid before returning it
