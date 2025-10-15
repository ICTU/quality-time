"""OWASP Dependency-Check JSON source version collector."""

from typing import TYPE_CHECKING, cast

from packaging.version import Version

from base_collectors import VersionCollector

from .base import OWASPDependencyCheckJSONBase
from .json_types import OWASPDependencyCheckJSON

if TYPE_CHECKING:
    from collector_utilities.type import Response


class OWASPDependencyCheckJSONSourceVersion(OWASPDependencyCheckJSONBase, VersionCollector):
    """Collector to collect the OWASP Dependency-Check version from the JSON report."""

    async def _parse_source_response_version(self, response: Response) -> Version:
        """Override to parse the OWASP Dependency-Check version from the JSON."""
        json = cast(OWASPDependencyCheckJSON, await response.json())
        self._check_report_schema(json)
        return Version(json.get("scanInfo", {}).get("engineVersion", ""))
