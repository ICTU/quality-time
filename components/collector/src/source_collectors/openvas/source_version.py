"""OpenVAS source version collector."""

from packaging.version import Version

from base_collectors import SourceVersionCollector, XMLFileSourceCollector
from collector_utilities.functions import parse_source_response_xml
from collector_utilities.type import Response


class OpenVASSourceVersion(XMLFileSourceCollector, SourceVersionCollector):
    """Collector to collect the OpenVAS version."""

    async def _parse_source_response_version(self, response: Response) -> Version:
        """Override to parse the version from the XML."""
        return Version((await parse_source_response_xml(response)).findtext("./report/omp/version") or "0")
