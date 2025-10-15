"""OpenVAS security warnings collector."""

from typing import TYPE_CHECKING, ClassVar

from base_collectors import SecurityWarningsSourceCollector, XMLFileSourceCollector
from collector_utilities.functions import parse_source_response_xml
from model import Entities, Entity, SourceResponses

if TYPE_CHECKING:
    from xml.etree.ElementTree import Element  # nosec # Element is not available from defusedxml, but only used as type


class OpenVASSecurityWarnings(SecurityWarningsSourceCollector, XMLFileSourceCollector):
    """Collector to get security warnings from OpenVAS."""

    MAKE_ENTITY_SEVERITY_VALUE_LOWER_CASE = True

    # Mapping of OpenVAS attribute names to the measurement entity attribute names:
    ATTRIBUTES: ClassVar[dict[str, str]] = {
        "name": "name",
        "description": "description",
        "host": "host",
        "port": "port",
        "threat": "severity",
    }

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Override to parse the security warnings from the OpenVAS XML."""
        entities = Entities()
        for response in responses:
            tree = await parse_source_response_xml(response)
            entities.extend([self.__entity(result) for result in tree.findall(".//results/result")])
        return entities

    @classmethod
    def __entity(cls, result: Element) -> Entity:
        """Create the entity from the OpenVAS result."""
        attributes = cls.ATTRIBUTES.items()
        kwargs = {entity_attr: result.findtext(result_attr, default="") for result_attr, entity_attr in attributes}
        oid = result.findall("nvt")[0].attrib["oid"]  # Object identifier of the network vulnerability test
        key = f"{kwargs['host']}:{kwargs['port']}:{oid}"
        return Entity(key=key, **kwargs)
