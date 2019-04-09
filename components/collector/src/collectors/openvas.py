"""OpenVAS metric collector."""

from datetime import datetime, timezone
from typing import List
from xml.etree.cElementTree import Element

from dateutil.parser import isoparse  # type: ignore
import requests

from ..collector import Collector
from ..type import Value, Units
from ..util import parse_source_response_xml


class OpenVASSecurityWarnings(Collector):
    """Collector to get security warnings from OpenVAS."""

    def parse_source_response_value(self, response: requests.Response, **parameters) -> Value:
        tree, _ = parse_source_response_xml(response)
        return str(len(self.results(tree, **parameters)))

    def parse_source_response_units(self, response: requests.Response, **parameters) -> Units:
        tree, _ = parse_source_response_xml(response)
        units = []
        for result in self.results(tree, **parameters):
            units.append(
                dict(key=result.attrib["id"], name=result.findtext("name"), description=result.findtext("description"),
                     host=result.findtext("host"), port=result.findtext("port"), severity=result.findtext("threat")))
        return units

    @staticmethod
    def results(element: Element, **parameters) -> List[Element]:
        """Return the results that have one of the severities specified in the parameters."""
        severities = parameters.get("severities") or ["log", "low", "medium", "high"]
        results = element.findall(".//results/result")
        return [result for result in results if result.findtext("threat").lower() in severities]


class OpenVASSourceUpToDateness(Collector):
    """Collector to collect the OpenVAS report age."""

    def parse_source_response_value(self, response: requests.Response, **parameters) -> Value:
        tree, _ = parse_source_response_xml(response)
        report_datetime = isoparse(tree.findtext("creation_time"))
        return str((datetime.now(timezone.utc) - report_datetime).days)
