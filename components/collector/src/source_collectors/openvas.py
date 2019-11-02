"""OpenVAS metric collector."""

from abc import ABC
from datetime import datetime
from typing import List
from xml.etree.ElementTree import Element  # nosec, Element is not available from defusedxml, but only used as type

from dateutil.parser import isoparse

from collector_utilities.type import Entities, Response, Responses, Value
from collector_utilities.functions import parse_source_response_xml
from .source_collector import FileSourceCollector, SourceUpToDatenessCollector


class OpenVASBaseClass(FileSourceCollector, ABC):  # pylint: disable=abstract-method
    """Base class for Open VAS collectors."""

    file_extensions = ["xml"]


class OpenVASSecurityWarnings(OpenVASBaseClass):
    """Collector to get security warnings from OpenVAS."""

    def _parse_source_responses_value(self, responses: Responses) -> Value:
        return str(sum(len(self.__results(parse_source_response_xml(response))) for response in responses))

    def _parse_source_responses_entities(self, responses: Responses) -> Entities:
        entities: Entities = []
        for response in responses:
            tree = parse_source_response_xml(response)
            entities.extend(
                [dict(key=result.attrib["id"], name=result.findtext("name", default=""),
                      description=result.findtext("description", default=""),
                      host=result.findtext("host", default=""), port=result.findtext("port", default=""),
                      severity=result.findtext("threat", default=""))
                 for result in self.__results(tree)])
        return entities

    def __results(self, element: Element) -> List[Element]:
        """Return the results that have one of the severities specified in the parameters."""
        severities = self._parameter("severities")
        results = element.findall(".//results/result")
        return [result for result in results if result.findtext("threat", default="").lower() in severities]


class OpenVASSourceUpToDateness(OpenVASBaseClass, SourceUpToDatenessCollector):
    """Collector to collect the OpenVAS report age."""

    def _parse_source_response_date_time(self, response: Response) -> datetime:
        tree = parse_source_response_xml(response)
        return isoparse(tree.findtext("creation_time", default=""))
