"""OpenVAS metric collector."""

from typing import List
from xml.etree.ElementTree import Element  # nosec, Element is not available from defusedxml, but only used as type

from dateutil.parser import isoparse  # type: ignore
import requests

from ..source_collectors.source_collector import SourceCollector
from ..utilities.type import Value, Entities
from ..utilities.functions import days_ago, parse_source_response_xml


class OpenVASSecurityWarnings(SourceCollector):
    """Collector to get security warnings from OpenVAS."""

    def parse_source_responses_value(self, responses: List[requests.Response]) -> Value:
        tree = parse_source_response_xml(responses[0])
        return str(len(self.results(tree)))

    def parse_source_responses_entities(self, responses: List[requests.Response]) -> Entities:
        tree = parse_source_response_xml(responses[0])
        return [dict(key=result.attrib["id"], name=result.findtext("name"), description=result.findtext("description"),
                     host=result.findtext("host"), port=result.findtext("port"), severity=result.findtext("threat"))
                for result in self.results(tree)]

    def results(self, element: Element) -> List[Element]:
        """Return the results that have one of the severities specified in the parameters."""
        severities = self.parameters.get("severities") or ["log", "low", "medium", "high"]
        results = element.findall(".//results/result")
        return [result for result in results if result.findtext("threat").lower() in severities]


class OpenVASSourceUpToDateness(SourceCollector):
    """Collector to collect the OpenVAS report age."""

    def parse_source_responses_value(self, responses: List[requests.Response]) -> Value:
        tree = parse_source_response_xml(responses[0])
        report_datetime = isoparse(tree.findtext("creation_time"))
        return str(days_ago(report_datetime))
