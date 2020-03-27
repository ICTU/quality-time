"""OWASP Dependency Check Jenkins plugin metric collector."""

from typing import Dict, Tuple

from collector_utilities.type import Entities, Entity, Responses, Value, URL
from base_collectors import JenkinsPluginSourceUpToDatenessCollector, SourceCollector


class OWASPDependencyCheckJenkinsPluginSecurityWarnings(SourceCollector):
    """OWASP Dependency Check Jenkins plugin security warnings collector."""

    async def _api_url(self) -> URL:
        api_url = await super()._api_url()
        return URL(f"{api_url}/lastSuccessfulBuild/dependency-check-jenkins-pluginResult/api/json?depth=1")

    async def _landing_url(self, responses: Responses) -> URL:
        return URL(f"{await super()._api_url()}/lastSuccessfulBuild/dependency-check-jenkins-pluginResult")

    async def _parse_source_responses(self, responses: Responses) -> Tuple[Value, Value, Entities]:
        json = await responses[0].json()
        severities = self._parameter("severities")
        warnings = [warning for warning in json.get("warnings", []) if warning["priority"].lower() in severities]
        entities: Dict[str, Entity] = dict()
        for warning in warnings:
            priority = warning["priority"].lower()
            file_path = warning["fileName"]
            if file_path in entities:
                entities[file_path]["nr_vulnerabilities"] = int(entities[file_path]["nr_vulnerabilities"]) + 1
                entities[file_path]["highest_severity"] = \
                    self.__highest_severity(str(entities[file_path]["highest_severity"]).lower(), priority).capitalize()
            else:
                entities[file_path] = dict(
                    key=file_path, file_path=file_path, highest_severity=priority.capitalize(), nr_vulnerabilities=1)
        return str(len(entities)), "100", list(entities.values())

    def __highest_severity(self, severity1: str, severity2: str) -> str:
        """Return the highest of the two severities."""
        severities = self._datamodel["sources"][self.source_type]["parameters"]["severities"]["values"]
        return severity1 if severities.index(severity1) >= severities.index(severity2) else severity2


class OWASPDependencyCheckJenkinsPluginSourceUpToDateness(JenkinsPluginSourceUpToDatenessCollector):
    """Collector to get the age of the OWASP Dependency Check Jenkins plugin report."""
