"""OWASP Dependency-Check XML dependencies collector."""

from typing import cast
from xml.etree.ElementTree import Element  # nosec # Element is not available from defusedxml, but only used as type

from collector_utilities.functions import parse_source_response_xml_with_namespace, sha1_hash, stabilize
from collector_utilities.type import Namespaces
from model import Entities, Entity, SourceResponses

from .base import OWASPDependencyCheckXMLBase


class OWASPDependencyCheckXMLDependencies(OWASPDependencyCheckXMLBase):
    """Collector to get the dependencies from the OWASP Dependency-Check XML report."""

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Override to parse the dependencies from the XML."""
        landing_url = await self._landing_url(responses)
        entities = Entities()
        for response in responses:
            tree, namespaces = await parse_source_response_xml_with_namespace(response, self.allowed_root_tags)
            entities.extend(
                [
                    self._parse_entity(dependency, index, namespaces, landing_url)
                    for (index, dependency) in enumerate(self._dependencies(tree, namespaces))
                ],
            )
        return entities

    def _dependencies(self, tree: Element, namespaces: Namespaces) -> list[Element]:
        """Return the dependencies."""
        return tree.findall(".//ns:dependency", namespaces)

    def _parse_entity(
        self,
        dependency: Element,
        dependency_index: int,
        namespaces: Namespaces,
        landing_url: str,
    ) -> Entity:
        """Parse the entity from the dependency."""
        file_path = dependency.findtext("ns:filePath", default="", namespaces=namespaces)
        stable_file_path = stabilize(file_path.strip(), cast(list[str], self._parameter("variable_file_path_regexp")))
        file_name = dependency.findtext("ns:fileName", default="", namespaces=namespaces)
        sha1 = dependency.findtext("ns:sha1", namespaces=namespaces)
        # We can only generate an entity landing url if a sha1 is present in the XML, but unfortunately not all
        # dependencies have one, so check for it:
        entity_landing_url = f"{landing_url}#l{dependency_index + 1}_{sha1}" if sha1 else ""
        key = sha1 if sha1 else sha1_hash(stable_file_path + file_name)
        return Entity(
            key=key,
            file_path=file_path,
            file_path_after_regexp=stable_file_path,
            file_name=file_name,
            url=entity_landing_url,
        )
