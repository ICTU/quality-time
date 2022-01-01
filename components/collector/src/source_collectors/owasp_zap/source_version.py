"""OWASP ZAP source version collector."""

from packaging.version import Version

from base_collectors import SourceVersionCollector, XMLFileSourceCollector
from collector_utilities.functions import parse_source_response_xml
from collector_utilities.type import Response


class OWASPZAPSourceVersion(XMLFileSourceCollector, SourceVersionCollector):
    """Collector to collect the OWASP ZAP version."""

    async def _parse_source_response_version(self, response: Response) -> Version:
        """Override to parse the version from the XML."""
        version_text = (await parse_source_response_xml(response)).get("version") or "0"
        if version_text.startswith("D-"):
            version_text = version_text.removeprefix("D-").replace("-", ".")
        return Version(version_text)
