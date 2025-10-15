"""OWASP ZAP source version collector."""

from typing import TYPE_CHECKING

from packaging.version import Version

from base_collectors import VersionCollector, XMLFileSourceCollector
from collector_utilities.functions import parse_source_response_xml

if TYPE_CHECKING:
    from collector_utilities.type import Response


class OWASPZAPSourceVersion(XMLFileSourceCollector, VersionCollector):
    """Collector to collect the OWASP ZAP version."""

    async def _parse_source_response_version(self, response: Response) -> Version:
        """Override to parse the version from the XML."""
        version_text = (await parse_source_response_xml(response)).get("version") or "0"
        if version_text.startswith("D-"):
            version_text = version_text.removeprefix("D-").replace("-", ".")
        return Version(version_text)
