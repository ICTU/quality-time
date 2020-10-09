"""OWASP Dependency Check Jenkins plugin metric collector."""

from typing import Dict

from base_collectors import JenkinsPluginCollector, JenkinsPluginSourceUpToDatenessCollector
from source_model import Entity, SourceMeasurement, SourceResponses


class OWASPDependencyCheckJenkinsPluginSecurityWarnings(JenkinsPluginCollector):
    """OWASP Dependency Check Jenkins plugin security warnings collector."""

    plugin = "dependency-check-jenkins-pluginResult"
    depth = 1

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        json = await responses[0].json()
        severities = self._parameter("severities")
        warnings = [warning for warning in json.get("warnings", []) if warning["priority"].lower() in severities]
        entities: Dict[str, Entity] = {}
        for warning in warnings:
            priority = warning["priority"].lower()
            file_path = warning["fileName"]
            if file_path in entities:
                entities[file_path]["nr_vulnerabilities"] = str(int(entities[file_path]["nr_vulnerabilities"]) + 1)
                entities[file_path]["highest_severity"] = \
                    self.__highest_severity(str(entities[file_path]["highest_severity"]).lower(), priority).capitalize()
            else:
                entities[file_path] = Entity(
                    key=file_path, file_path=file_path, highest_severity=priority.capitalize(), nr_vulnerabilities="1")
        return SourceMeasurement(entities=list(entities.values()))

    def __highest_severity(self, severity1: str, severity2: str) -> str:
        """Return the highest of the two severities."""
        severities = self._data_model["sources"][self.source_type]["parameters"]["severities"]["values"]
        return severity1 if severities.index(severity1) >= severities.index(severity2) else severity2


class OWASPDependencyCheckJenkinsPluginSourceUpToDateness(JenkinsPluginSourceUpToDatenessCollector):
    """Collector to get the age of the OWASP Dependency Check Jenkins plugin report."""
