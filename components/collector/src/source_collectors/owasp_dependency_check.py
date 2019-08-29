"""OWASP Dependency Check metric collector."""

import hashlib
from typing import List, Tuple
from xml.etree.ElementTree import Element  # nosec, Element is not available from defusedxml, but only used as type

from dateutil.parser import isoparse
import requests

from utilities.type import Namespaces, Entity, Entities, Value
from utilities.functions import days_ago, parse_source_response_xml_with_namespace
from .source_collector import SourceCollector


class OWASPDependencyCheckBase(SourceCollector):
    """Base class for OWASP Dependency Check collectors."""

    allowed_root_tags = [f"{{https://jeremylong.github.io/DependencyCheck/dependency-check.{version}.xsd}}analysis"
                         for version in ("2.0", "2.1", "2.2")]


class OWASPDependencyCheckSecurityWarnings(OWASPDependencyCheckBase):
    """Collector to get security warnings from OWASP Dependency Check."""

    def _parse_source_responses_value(self, responses: List[requests.Response]) -> Value:
        tree, namespaces = parse_source_response_xml_with_namespace(responses[0], self.allowed_root_tags)
        return str(len(self.__vulnerable_dependencies(tree, namespaces)))

    def __vulnerable_dependencies(self, tree: Element, namespaces: Namespaces) -> List[Tuple[int, Element]]:
        """Return the vulnerable dependencies."""
        return [(index, dependency) for (index, dependency) in enumerate(tree.findall(".//ns:dependency", namespaces))
                if self.__vulnerabilities(dependency, namespaces)]

    def _parse_source_responses_entities(self, responses: List[requests.Response]) -> Entities:
        tree, namespaces = parse_source_response_xml_with_namespace(responses[0], self.allowed_root_tags)
        landing_url = self._landing_url(responses)
        return [self.__parse_entity(dependency, index, namespaces, landing_url) for (index, dependency)
                in self.__vulnerable_dependencies(tree, namespaces)]

    def __parse_entity(
            self, dependency: Element, dependency_index: int, namespaces: Namespaces, landing_url: str) -> Entity:
        """Parse the entity from the dependency."""
        file_path = dependency.findtext("ns:filePath", default="", namespaces=namespaces)
        sha1 = dependency.findtext("ns:sha1", namespaces=namespaces)
        # We can only generate a entity landing url if a sha1 is present in the XML, but unfortunately not all
        # dependencies have one, so check for it:
        entity_landing_url = f"{landing_url}#l{dependency_index + 1}_{sha1}" if sha1 else ""
        key = sha1 if sha1 else hashlib.sha1(bytes(file_path, "utf8")).hexdigest()  # nosec, Not used for cryptography
        vulnerabilities = self.__vulnerabilities(dependency, namespaces)
        severities = set(vulnerability.findtext(".//ns:severity", default="", namespaces=namespaces).lower()
                         for vulnerability in vulnerabilities)
        highest_severity = "low"
        for severity in ("critical", "high", "medium"):
            if severity in severities:
                highest_severity = severity
                break
        return dict(key=key, file_path=file_path, highest_severity=highest_severity.capitalize(),
                    url=entity_landing_url, nr_vulnerabilities=len(vulnerabilities))

    def __vulnerabilities(self, element: Element, namespaces: Namespaces) -> List[Element]:
        """Return the vulnerabilities that have one of the severities specified in the parameters."""
        severities = self._parameter("severities")
        vulnerabilities = element.findall(".//ns:vulnerabilities/ns:vulnerability", namespaces)
        return [vulnerability for vulnerability in vulnerabilities if
                vulnerability.findtext(".//ns:severity", default="", namespaces=namespaces).lower() in severities]


class OWASPDependencyCheckSourceUpToDateness(OWASPDependencyCheckBase):
    """Collector to collect the OWASP Dependency Check report age."""

    def _parse_source_responses_value(self, responses: List[requests.Response]) -> Value:
        tree, namespaces = parse_source_response_xml_with_namespace(responses[0], self.allowed_root_tags)
        report_datetime = isoparse(tree.findtext(".//ns:reportDate", default="", namespaces=namespaces))
        return str(days_ago(report_datetime))
