"""OWASP Dependency-Check JSON source version collector."""

from typing import TYPE_CHECKING

from packaging.version import Version

from base_collectors import VersionCollector

from .base import OWASPDependencyCheckJSONBase

if TYPE_CHECKING:
    from collector_utilities.type import Response


class OWASPDependencyCheckJSONSourceVersion(OWASPDependencyCheckJSONBase, VersionCollector):
    """Collector to collect the OWASP Dependency-Check version from the JSON report."""

    async def _parse_source_response_version(self, response: Response) -> Version:
        """Override to parse the OWASP Dependency-Check version from the JSON."""
        json = await self._json(response)
        return Version(json.get("scanInfo", {}).get("engineVersion", ""))
