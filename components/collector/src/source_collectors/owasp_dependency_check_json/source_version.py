"""OWASP Dependency-Check JSON source version collector."""

from typing import cast

from packaging.version import Version

from base_collectors import VersionCollector
from collector_utilities.type import Response

from .base import OWASPDependencyCheckJSON, OWASPDependencyCheckJSONBase


class OWASPDependencyCheckJSONSourceVersion(OWASPDependencyCheckJSONBase, VersionCollector):
    """Collector to collect the OWASP Dependency-Check version from the JSON report."""

    async def _parse_source_response_version(self, response: Response) -> Version:
        """Override to parse the OWASP Dependency-Check version from the JSON."""
        json = cast(OWASPDependencyCheckJSON, await response.json())
        self._check_report_schema(json)
        return Version(json.get("scanInfo", {}).get("engineVersion", ""))
