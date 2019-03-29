"""OWASP Dependency Check metric collector."""

import requests

from ..collector import Collector
from ..type import Units, URL, Value
from ..util import parse_source_response_xml


class OWASPDependencyCheckSecurityWarnings(Collector):
    """Collector to get security warnings from OWASP Dependency Check."""

    def landing_url(self, **parameters) -> URL:
        return URL(parameters["url"][:-(len("xml"))] + "html")

    def parse_source_response_value(self, response: requests.Response, **parameters) -> Value:
        tree, namespaces = parse_source_response_xml(response)
        severities = parameters.get("severities") or ["low", "medium", "high"]
        vulnerabilities = []
        for severity in severities:
            vulnerabilities.extend(
                tree.findall(
                    f".//ns:dependency/ns:vulnerabilities/ns:vulnerability[ns:severity='{severity.capitalize()}']",
                    namespaces))
        return str(len(vulnerabilities))

    def parse_source_response_units(self, response: requests.Response, **parameters) -> Units:
        tree, namespaces = parse_source_response_xml(response)
        severities = parameters.get("severities") or ["low", "medium", "high"]
        units = []
        for dependency in tree.findall(".//ns:dependency", namespaces):
            file_path = dependency.findtext("ns:filePath", namespaces=namespaces)
            for severity in severities:
                for vulnerability in dependency.findall(
                        f"./ns:vulnerabilities/ns:vulnerability[ns:severity='{severity.capitalize()}']", namespaces):
                    key = ":".join([file_path, vulnerability.findtext("ns:name", namespaces=namespaces)])
                    units.append(
                        dict(key=key, location=file_path, name=vulnerability.findtext("ns:name", namespaces=namespaces),
                             description=vulnerability.findtext("ns:description", namespaces=namespaces),
                             severity=vulnerability.findtext("ns:severity", namespaces=namespaces)))
        return units
