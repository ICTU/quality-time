"""OpenVAS security warnings collector."""

from typing import cast
from xml.etree.ElementTree import Element  # nosec # Element is not available from defusedxml, but only used as type

from base_collectors import XMLFileSourceCollector
from collector_utilities.functions import parse_source_response_xml
from model import Entities, Entity, SourceResponses


class OpenVASSecurityWarnings(XMLFileSourceCollector):
    """Collector to get security warnings from OpenVAS."""

    # Mapping of OpenVAS attribute names to the measurement entity attribute names:
    ATTRIBUTES = dict(name="name", description="description", host="host", port="port", threat="severity")

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Override to parse the security warnings from the OpenVAS XML."""
        entities = Entities()
        severities = cast(list[str], self._parameter("severities"))
        for response in responses:
            tree = await parse_source_response_xml(response)
            entities.extend([self.__entity(result) for result in self.__results(tree, severities)])
        return entities

    @classmethod
    def __entity(cls, result: Element) -> Entity:
        """Create the entity from the OpenVAS result."""
        attributes = cls.ATTRIBUTES.items()
        kwargs = {entity_attr: result.findtext(result_attr, default="") for result_attr, entity_attr in attributes}
        oid = result.findall("nvt")[0].attrib["oid"]  # Object identifier of the network vulnerability test
        key = f"{kwargs['host']}:{kwargs['port']}:{oid}"
        return Entity(key=key, **kwargs)

    @staticmethod
    def __results(element: Element, severities: list[str]) -> list[Element]:
        """Return the results that have one of the severities specified in the parameters."""
        results = element.findall(".//results/result")
        return [result for result in results if result.findtext("threat", default="").lower() in severities]
