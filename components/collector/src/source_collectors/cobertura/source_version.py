"""Cobertura coverage report source version collector."""

from packaging.version import Version

from base_collectors import SourceVersionCollector, XMLFileSourceCollector
from collector_utilities.functions import parse_source_response_xml
from collector_utilities.type import Response


class CoberturaSourceVersion(XMLFileSourceCollector, SourceVersionCollector):
    """Collector to collect the Cobertura report version."""

    async def _parse_source_response_version(self, response: Response) -> Version:
        """Override to parse the version from the response."""
        tree = await parse_source_response_xml(response)
        return Version(tree.get("version") or "0")
