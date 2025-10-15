"""OWASP Dependency-Check XML source up-to-dateness collector."""

from typing import TYPE_CHECKING

from base_collectors import TimePassedCollector
from collector_utilities.date_time import parse_datetime
from collector_utilities.functions import parse_source_response_xml_with_namespace

from .base import OWASPDependencyCheckXMLBase

if TYPE_CHECKING:
    from datetime import datetime

    from collector_utilities.type import Response


class OWASPDependencyCheckXMLSourceUpToDateness(OWASPDependencyCheckXMLBase, TimePassedCollector):
    """Collector to collect the OWASP Dependency-Check XML report age."""

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        """Override to parse the report date from the XML."""
        tree, namespaces = await parse_source_response_xml_with_namespace(response, self.allowed_root_tags)
        return parse_datetime(tree.findtext(".//ns:reportDate", default="", namespaces=namespaces))
