"""OWASP Dependency Check metric collector."""

from abc import ABC
from datetime import datetime
from typing import List
from xml.etree.ElementTree import Element  # nosec, Element is not available from defusedxml, but only used as type

from dateutil.parser import isoparse

from collector_utilities.type import Namespaces, Entity, Response
from collector_utilities.functions import sha1_hash, parse_source_response_xml_with_namespace
from base_collectors import XMLFileSourceCollector, SourceMeasurement, SourceResponses, SourceUpToDatenessCollector


class OWASPDependencyCheckBase(XMLFileSourceCollector, ABC):  # pylint: disable=abstract-method
    """Base class for OWASP Dependency Check collectors."""

    allowed_root_tags = [f"{{https://jeremylong.github.io/DependencyCheck/dependency-check.{version}.xsd}}analysis"
                         for version in ("2.0", "2.1", "2.2", "2.3")]


class OWASPDependencyCheckDependencies(OWASPDependencyCheckBase):
    """Collector to get the dependencies from the OWASP Dependency Check XML report."""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        landing_url = await self._landing_url(responses)
        entities = []
        for response in responses:
            tree, namespaces = await parse_source_response_xml_with_namespace(response, self.allowed_root_tags)
            entities.extend(
                [self._parse_entity(dependency, index, namespaces, landing_url) for (index, dependency)
                 in enumerate(self._dependencies(tree, namespaces))])
        return SourceMeasurement(entities=entities)

    def _dependencies(self, tree: Element, namespaces: Namespaces) -> List[Element]:  # pylint: disable=no-self-use
        """Return the dependencies."""
        return tree.findall(".//ns:dependency", namespaces)

    def _parse_entity(  # pylint: disable=no-self-use
            self, dependency: Element, dependency_index: int, namespaces: Namespaces, landing_url: str) -> Entity:
        """Parse the entity from the dependency."""
        file_path = dependency.findtext("ns:filePath", default="", namespaces=namespaces)
        sha1 = dependency.findtext("ns:sha1", namespaces=namespaces)
        # We can only generate a entity landing url if a sha1 is present in the XML, but unfortunately not all
        # dependencies have one, so check for it:
        entity_landing_url = f"{landing_url}#l{dependency_index + 1}_{sha1}" if sha1 else ""
        key = sha1 if sha1 else sha1_hash(file_path)
        return dict(key=key, file_path=file_path, url=entity_landing_url)


class OWASPDependencyCheckSecurityWarnings(OWASPDependencyCheckDependencies):
    """Collector to get security warnings from the OWASP Dependency Check XML report."""

    def _dependencies(self, tree: Element, namespaces: Namespaces) -> List[Element]:
        """Return the vulnerable dependencies."""
        return [
            dependency for dependency in tree.findall(".//ns:dependency", namespaces)
            if self.__vulnerabilities(dependency, namespaces)]

    def _parse_entity(
            self, dependency: Element, dependency_index: int, namespaces: Namespaces, landing_url: str) -> Entity:
        """Parse the entity from the dependency."""
        entity = super()._parse_entity(dependency, dependency_index, namespaces, landing_url)
        vulnerabilities = self.__vulnerabilities(dependency, namespaces)
        severities = set(vulnerability.findtext(".//ns:severity", default="", namespaces=namespaces).lower()
                         for vulnerability in vulnerabilities)
        highest_severity = "low"
        for severity in ("critical", "high", "medium"):
            if severity in severities:
                highest_severity = severity
                break
        entity.update(
            dict(highest_severity=highest_severity.capitalize(), nr_vulnerabilities=str(len(vulnerabilities))))
        return entity

    def __vulnerabilities(self, element: Element, namespaces: Namespaces) -> List[Element]:
        """Return the vulnerabilities that have one of the severities specified in the parameters."""
        severities = self._parameter("severities")
        vulnerabilities = element.findall(".//ns:vulnerabilities/ns:vulnerability", namespaces)
        return [vulnerability for vulnerability in vulnerabilities if
                vulnerability.findtext(".//ns:severity", default="", namespaces=namespaces).lower() in severities]


class OWASPDependencyCheckSourceUpToDateness(OWASPDependencyCheckBase, SourceUpToDatenessCollector):
    """Collector to collect the OWASP Dependency Check report age."""

    async def _parse_source_response_date_time(self, response: Response) -> datetime:
        tree, namespaces = await parse_source_response_xml_with_namespace(response, self.allowed_root_tags)
        return isoparse(tree.findtext(".//ns:reportDate", default="", namespaces=namespaces))
