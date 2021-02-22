"""OpenVAS security warnings collector."""

from typing import cast
from xml.etree.ElementTree import Element  # nosec, Element is not available from defusedxml, but only used as type

from base_collectors import XMLFileSourceCollector
from collector_utilities.functions import parse_source_response_xml
from source_model import Entity, SourceMeasurement, SourceResponses


class OpenVASSecurityWarnings(XMLFileSourceCollector):
    """Collector to get security warnings from OpenVAS."""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the security warnings from the OpenVAS XML."""
        entities = []
        severities = cast(list[str], self._parameter("severities"))
        for response in responses:
            tree = await parse_source_response_xml(response)
            entities.extend(
                [
                    Entity(
                        key=result.attrib["id"],
                        name=result.findtext("name", default=""),
                        description=result.findtext("description", default=""),
                        host=result.findtext("host", default=""),
                        port=result.findtext("port", default=""),
                        severity=result.findtext("threat", default=""),
                    )
                    for result in self.__results(tree, severities)
                ]
            )
        return SourceMeasurement(entities=entities)

    @staticmethod
    def __results(element: Element, severities: list[str]) -> list[Element]:
        """Return the results that have one of the severities specified in the parameters."""
        results = element.findall(".//results/result")
        return [result for result in results if result.findtext("threat", default="").lower() in severities]
