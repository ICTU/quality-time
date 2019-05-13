"""OWASP Dependency Check metric collector."""

import hashlib
from typing import List, Tuple
from xml.etree.cElementTree import Element

from dateutil.parser import isoparse  # type: ignore
import requests

from ..collector import Collector
from ..type import Namespaces, Entity, Entities, Value
from ..util import days_ago, parse_source_response_xml_with_namespace


class OWASPDependencyCheckSecurityWarnings(Collector):
    """Collector to get security warnings from OWASP Dependency Check."""

    def parse_source_response_value(self, response: requests.Response, **parameters) -> Value:
        tree, namespaces = parse_source_response_xml_with_namespace(response)
        return str(len(self.vulnerable_dependencies(tree, namespaces, **parameters)))

    def vulnerable_dependencies(self, tree: Element, namespaces: Namespaces, **parameters) -> List[Tuple[int, Element]]:
        """Return the vulnerable dependencies."""
        return [(index, dependency) for (index, dependency) in enumerate(tree.findall(".//ns:dependency", namespaces))
                if self.vulnerabilities(dependency, namespaces, **parameters)]

    def parse_source_response_entities(self, response: requests.Response, **parameters) -> Entities:
        tree, namespaces = parse_source_response_xml_with_namespace(response)
        landing_url = self.landing_url(response, **parameters)
        return [self.parse_entity(dependency, index, namespaces, landing_url, ** parameters) for (index, dependency)
                in self.vulnerable_dependencies(tree, namespaces, **parameters)]

    def parse_entity(self, dependency: Element, dependency_index: int, namespaces: Namespaces, landing_url: str,
                     **parameters) -> Entity:
        """Parse the entity from the dependency."""
        file_path = dependency.findtext("ns:filePath", namespaces=namespaces)
        sha1 = dependency.findtext('ns:sha1', namespaces=namespaces)
        # We can only generate a entity landing url if a sha1 is present in the XML, but unfortunately not all
        # dependencies have one, so check for it:
        entity_landing_url = f"{landing_url}#l{dependency_index + 1}_{sha1}" if sha1 else ""
        key = sha1 if sha1 else hashlib.sha1(bytes(file_path, "utf8")).hexdigest()
        vulnerabilities = self.vulnerabilities(dependency, namespaces, **parameters)
        severities = set(vulnerability.findtext(".//ns:severity", namespaces=namespaces).lower()
                         for vulnerability in vulnerabilities)
        highest_severity = "high" if "high" in severities else "medium" if "medium" in severities else "low"
        return dict(key=key, file_path=file_path, highest_severity=highest_severity.capitalize(),
                    url=entity_landing_url, nr_vulnerabilities=len(vulnerabilities))

    @staticmethod
    def vulnerabilities(element: Element, namespaces: Namespaces, **parameters) -> List[Element]:
        """Return the vulnerabilities that have one of the severities specified in the parameters."""
        severities = parameters.get("severities") or ["low", "medium", "high"]
        vulnerabilities = element.findall(".//ns:vulnerabilities/ns:vulnerability", namespaces)
        return [vulnerability for vulnerability in vulnerabilities if
                vulnerability.findtext(".//ns:severity", namespaces=namespaces).lower() in severities]


class OWASPDependencyCheckSourceUpToDateness(Collector):
    """Collector to collect the OWASP Dependency Check report age."""

    def parse_source_response_value(self, response: requests.Response, **parameters) -> Value:
        tree, namespaces = parse_source_response_xml_with_namespace(response)
        report_datetime = isoparse(tree.findtext(".//ns:reportDate", namespaces=namespaces))
        return str(days_ago(report_datetime))
