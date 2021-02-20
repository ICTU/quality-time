"""OWASP Dependency Check dependencies collector."""

from typing import List
from xml.etree.ElementTree import Element  # nosec, Element is not available from defusedxml, but only used as type

from collector_utilities.functions import parse_source_response_xml_with_namespace, sha1_hash
from collector_utilities.type import Namespaces
from source_model import Entity, SourceMeasurement, SourceResponses

from .base import OWASPDependencyCheckBase


class OWASPDependencyCheckDependencies(OWASPDependencyCheckBase):
    """Collector to get the dependencies from the OWASP Dependency Check XML report."""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the dependencies from the XML."""
        landing_url = await self._landing_url(responses)
        entities = []
        for response in responses:
            tree, namespaces = await parse_source_response_xml_with_namespace(response, self.allowed_root_tags)
            entities.extend(
                [
                    self._parse_entity(dependency, index, namespaces, landing_url)
                    for (index, dependency) in enumerate(self._dependencies(tree, namespaces))
                ]
            )
        return SourceMeasurement(entities=entities)

    def _dependencies(self, tree: Element, namespaces: Namespaces) -> List[Element]:  # pylint: disable=no-self-use
        """Return the dependencies."""
        return tree.findall(".//ns:dependency", namespaces)

    def _parse_entity(  # pylint: disable=no-self-use
        self, dependency: Element, dependency_index: int, namespaces: Namespaces, landing_url: str
    ) -> Entity:
        """Parse the entity from the dependency."""
        file_path = dependency.findtext("ns:filePath", default="", namespaces=namespaces)
        file_name = dependency.findtext("ns:fileName", default="", namespaces=namespaces)
        sha1 = dependency.findtext("ns:sha1", namespaces=namespaces)
        # We can only generate an entity landing url if a sha1 is present in the XML, but unfortunately not all
        # dependencies have one, so check for it:
        entity_landing_url = f"{landing_url}#l{dependency_index + 1}_{sha1}" if sha1 else ""
        key = sha1 if sha1 else sha1_hash(file_path + file_name)
        return Entity(key=key, file_path=file_path, file_name=file_name, url=entity_landing_url)
