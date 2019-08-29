"""OWASP Dependency Check Jenkins plugin metric collector."""

from datetime import datetime
from typing import Dict, List

import requests

from utilities.functions import days_ago
from utilities.type import Entities, Entity, Value, URL
from .source_collector import SourceCollector


class OWASPDependencyCheckJenkinsPluginSecurityWarnings(SourceCollector):
    """OWASP Dependency Check Jenkins plugin security warnings collector."""

    def _api_url(self) -> URL:
        return URL(f"{super()._api_url()}/lastSuccessfulBuild/dependency-check-jenkins-pluginResult/api/json?depth=1")

    def _landing_url(self, responses: List[requests.Response]) -> URL:
        return URL(f"{super()._api_url()}/lastSuccessfulBuild/dependency-check-jenkins-pluginResult")

    def _parse_source_responses_value(self, responses: List[requests.Response]) -> Value:
        return str(len(self._parse_source_responses_entities(responses)))

    def _parse_source_responses_entities(self, responses: List[requests.Response]) -> Entities:
        json = responses[0].json()
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
        return list(entities.values())

    def __highest_severity(self, severity1: str, severity2: str) -> str:
        """Return the highest of the two severities."""
        severities = self.datamodel["sources"][self.source_type]["parameters"]["severities"]["values"]
        return severity1 if severities.index(severity1) >= severities.index(severity2) else severity2


class OWASPDependencyCheckJenkinsPluginSourceUpToDateness(SourceCollector):
    """Collector to get the age of the OWASP Dependency Check Jenkins plugin report."""

    def _api_url(self) -> URL:
        return URL(f"{super()._api_url()}/lastSuccessfulBuild/api/json")

    def _parse_source_responses_value(self, responses: List[requests.Response]) -> Value:
        job_datetime = datetime.fromtimestamp(float(responses[0].json()["timestamp"]) / 1000.)
        return str(days_ago(job_datetime))
