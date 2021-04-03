"""OWASP Dependency Check source version collector."""

from packaging.version import Version

from base_collectors import SourceVersionCollector
from collector_utilities.functions import parse_source_response_xml_with_namespace
from collector_utilities.type import Response

from .base import OWASPDependencyCheckBase


class OWASPDependencyCheckSourceVersion(OWASPDependencyCheckBase, SourceVersionCollector):
    """Collector to collect the OWASP Dependency Check version from the report."""

    async def _parse_source_response_version(self, response: Response) -> Version:
        """Override to parse the OWASP Dependency Check version from the XML."""
        tree, namespaces = await parse_source_response_xml_with_namespace(response, self.allowed_root_tags)
        return Version(tree.findtext(".//ns:engineVersion", default="", namespaces=namespaces))
