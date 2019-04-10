"""OWASP Dependency Check metric collector."""

from typing import List
from xml.etree.cElementTree import Element

from dateutil.parser import isoparse  # type: ignore
import requests

from ..collector import Collector
from ..type import Namespaces, Units, Value
from ..util import days_ago, parse_source_response_xml_with_namespace


class OWASPDependencyCheckSecurityWarnings(Collector):
    """Collector to get security warnings from OWASP Dependency Check."""

    def parse_source_response_value(self, response: requests.Response, **parameters) -> Value:
        tree, namespaces = parse_source_response_xml_with_namespace(response)
        return str(len(self.vulnerabilities(tree, namespaces, **parameters)))

    def parse_source_response_units(self, response: requests.Response, **parameters) -> Units:
        tree, namespaces = parse_source_response_xml_with_namespace(response)
        units = []
        for dependency in tree.findall(".//ns:dependency", namespaces):
            file_path = dependency.findtext("ns:filePath", namespaces=namespaces)
            vulnerabilities = self.vulnerabilities(dependency, namespaces, **parameters)
            for vulnerability in vulnerabilities:
                key = ":".join([file_path, vulnerability.findtext("ns:name", namespaces=namespaces)])
                units.append(
                    dict(key=key, location=file_path, name=vulnerability.findtext("ns:name", namespaces=namespaces),
                         description=vulnerability.findtext("ns:description", namespaces=namespaces),
                         severity=vulnerability.findtext("ns:severity", namespaces=namespaces)))
        return units

    @staticmethod
    def vulnerabilities(element: Element, namespaces: Namespaces, **parameters) -> List[Element]:
        """Return the vulnerabilities that have one of the severities specified in the parameters."""
        severities = parameters.get("severities") or ["low", "medium", "high"]
        vulnerabilities = element.findall(".//ns:vulnerabilities/ns:vulnerability", namespaces)
        return [vulnerability for vulnerability in vulnerabilities if
                vulnerability.findtext("ns:severity", namespaces=namespaces).lower() in severities]


class OWASPDependencyCheckSourceUpToDateness(Collector):
    """Collector to collect the OWASP Dependency Check report age."""

    def parse_source_response_value(self, response: requests.Response, **parameters) -> Value:
        tree, namespaces = parse_source_response_xml_with_namespace(response)
        report_datetime = isoparse(tree.findtext(".//ns:reportDate", namespaces=namespaces))
        return str(days_ago(report_datetime))
