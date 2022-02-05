"""OWASP Dependency Check source up-to-dateness collector."""

from datetime import datetime

from dateutil.parser import isoparse

from base_collectors import TimePassedCollector
from collector_utilities.functions import parse_source_response_xml_with_namespace
from collector_utilities.type import Response

from .base import OWASPDependencyCheckBase


class OWASPDependencyCheckSourceUpToDateness(OWASPDependencyCheckBase, TimePassedCollector):
    """Collector to collect the OWASP Dependency Check report age."""

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        """Override to parse the report date from the XML."""
        tree, namespaces = await parse_source_response_xml_with_namespace(response, self.allowed_root_tags)
        return isoparse(tree.findtext(".//ns:reportDate", default="", namespaces=namespaces))
