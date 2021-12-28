"""Snyk metrics security warnings collector."""

from collections.abc import Collection
from typing import cast, Literal

from base_collectors import JSONFileSourceCollector
from collector_utilities.type import JSON, JSONDict
from model import Entities, Entity


Severity = Literal["low", "medium", "high"]


class SnykSecurityWarnings(JSONFileSourceCollector):
    """Snyk collector for security warnings."""

    def _parse_json(self, json: JSON, filename: str) -> Entities:
        """Parse the direct dependencies with vulnerabilities from the JSON."""
        selected_severities = self._parameter("severities")
        severities: dict[str, set[Severity]] = {}
        nr_vulnerabilities: dict[str, int] = {}
        example_vulnerability = {}
        vulnerabilities = cast(JSONDict, json).get("vulnerabilities", [])
        for vulnerability in vulnerabilities:
            if (severity := vulnerability["severity"]) not in selected_severities:
                continue
            dependency = vulnerability["from"][1] if len(vulnerability["from"]) > 1 else vulnerability["from"][0]
            severities.setdefault(dependency, set()).add(severity)
            nr_vulnerabilities[dependency] = nr_vulnerabilities.get(dependency, 0) + 1
            path = " ➜ ".join(str(dependency) for dependency in vulnerability["from"])
            example_vulnerability[dependency] = (vulnerability["id"], path)

        entities = Entities()
        for dependency, severity_set in severities.items():
            entities.append(
                Entity(
                    key=dependency,
                    dependency=dependency,
                    nr_vulnerabilities=nr_vulnerabilities[dependency],
                    example_vulnerability=example_vulnerability[dependency][0],
                    url=f"https://snyk.io/vuln/{example_vulnerability[dependency][0]}",
                    example_path=example_vulnerability[dependency][1],
                    highest_severity=self.__highest_severity(severity_set),
                )
            )
        return entities

    @staticmethod
    def __highest_severity(severities: Collection[Severity]) -> Severity:
        """Return the highest severity from a collection of severities."""
        if "high" in severities:
            return "high"
        if "medium" in severities:
            return "medium"
        return "low"
