"""OWASP Dependency-Check JSON security warnings collector."""

from model import Entity

from .dependencies import OWASPDependencyCheckJSONDependencies
from .json_types import Dependency, OWASPDependencyCheckJSON, Vulnerability


class OWASPDependencyCheckJSONSecurityWarnings(OWASPDependencyCheckJSONDependencies):
    """Collector to get security warnings from the OWASP Dependency-Check JSON report."""

    def _dependencies(self, owasp_dependency_check_json: OWASPDependencyCheckJSON) -> list[Dependency]:
        """Override to return vulnerable dependencies only."""
        dependencies = super()._dependencies(owasp_dependency_check_json)
        return [dependency for dependency in dependencies if self.__vulnerabilities(dependency)]

    def _parse_entity(self, dependency: Dependency, dependency_index: int, landing_url: str) -> Entity:
        """Parse the entity from the dependency."""
        entity = super()._parse_entity(dependency, dependency_index, landing_url)
        vulnerabilities = self.__vulnerabilities(dependency)
        severities = {vulnerability.get("severity", "").lower() for vulnerability in vulnerabilities}
        highest_severity = "low"
        for severity in ("critical", "high", "medium", "moderate"):
            if severity in severities:
                highest_severity = severity
                break
        entity.update(
            {"highest_severity": highest_severity.capitalize(), "nr_vulnerabilities": str(len(vulnerabilities))},
        )
        return entity

    def __vulnerabilities(self, dependency: Dependency) -> list[Vulnerability]:
        """Return the vulnerabilities that have one of the severities specified in the parameters."""
        severities = self._parameter("severities")
        vulnerabilities = dependency.get("vulnerabilities", [])
        return [
            vulnerability
            for vulnerability in vulnerabilities
            if vulnerability.get("severity", "").lower() in severities
        ]
