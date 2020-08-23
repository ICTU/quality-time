"""OpenVAS metric collector."""

from datetime import datetime
from typing import List, cast
from xml.etree.ElementTree import Element  # nosec, Element is not available from defusedxml, but only used as type

from dateutil.parser import isoparse

from base_collectors import SourceMeasurement, SourceResponses, SourceUpToDatenessCollector, XMLFileSourceCollector
from collector_utilities.functions import parse_source_response_xml
from collector_utilities.type import Entities, Response


class OpenVASSecurityWarnings(XMLFileSourceCollector):
    """Collector to get security warnings from OpenVAS."""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        entities: Entities = []
        severities = cast(List[str], self._parameter("severities"))
        for response in responses:
            tree = await parse_source_response_xml(response)
            entities.extend(
                [dict(key=result.attrib["id"], name=result.findtext("name", default=""),
                      description=result.findtext("description", default=""),
                      host=result.findtext("host", default=""), port=result.findtext("port", default=""),
                      severity=result.findtext("threat", default=""))
                 for result in self.__results(tree, severities)])
        return SourceMeasurement(entities=entities)

    @staticmethod
    def __results(element: Element, severities: List[str]) -> List[Element]:
        """Return the results that have one of the severities specified in the parameters."""
        results = element.findall(".//results/result")
        return [result for result in results if result.findtext("threat", default="").lower() in severities]


class OpenVASSourceUpToDateness(XMLFileSourceCollector, SourceUpToDatenessCollector):
    """Collector to collect the OpenVAS report age."""

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        tree = await parse_source_response_xml(response)
        return isoparse(tree.findtext("creation_time", default=""))
