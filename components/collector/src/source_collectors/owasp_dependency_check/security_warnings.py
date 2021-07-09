"""OWASP Dependency Check security warnings collector."""

from xml.etree.ElementTree import Element  # nosec, Element is not available from defusedxml, but only used as type

from collector_utilities.type import Namespaces
from source_model import Entity

from .dependencies import OWASPDependencyCheckDependencies


class OWASPDependencyCheckSecurityWarnings(OWASPDependencyCheckDependencies):
    """Collector to get security warnings from the OWASP Dependency Check XML report."""

    def _dependencies(self, tree: Element, namespaces: Namespaces) -> list[Element]:
        """Override to return vulnerable dependencies only."""
        return [
            dependency
            for dependency in tree.findall(".//ns:dependency", namespaces)
            if self.__vulnerabilities(dependency, namespaces)
        ]

    def _parse_entity(
        self, dependency: Element, dependency_index: int, namespaces: Namespaces, landing_url: str
    ) -> Entity:
        """Parse the entity from the dependency."""
        entity = super()._parse_entity(dependency, dependency_index, namespaces, landing_url)
        vulnerabilities = self.__vulnerabilities(dependency, namespaces)
        severities = {
            vulnerability.findtext(".//ns:severity", default="", namespaces=namespaces).lower()
            for vulnerability in vulnerabilities
        }
        highest_severity = "low"
        for severity in ("critical", "high", "medium", "moderate"):
            if severity in severities:
                highest_severity = severity
                break
        entity.update(
            dict(highest_severity=highest_severity.capitalize(), nr_vulnerabilities=str(len(vulnerabilities)))
        )
        return entity

    def __vulnerabilities(self, element: Element, namespaces: Namespaces) -> list[Element]:
        """Return the vulnerabilities that have one of the severities specified in the parameters."""
        severities = self._parameter("severities")
        vulnerabilities = element.findall(".//ns:vulnerabilities/ns:vulnerability", namespaces)
        return [
            vulnerability
            for vulnerability in vulnerabilities
            if vulnerability.findtext(".//ns:severity", default="", namespaces=namespaces).lower() in severities
        ]
