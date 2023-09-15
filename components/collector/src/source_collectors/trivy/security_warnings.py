"""Trivy JSON collector."""

from typing import TypedDict, cast

from base_collectors import JSONFileSourceCollector
from collector_utilities.type import JSON
from model import Entities, Entity

# The types below are based on https://aquasecurity.github.io/trivy/v0.45/docs/configuration/reporting/#json.
# That documentation says: "VulnerabilityID, PkgName, InstalledVersion, and Severity in Vulnerabilities are always
# filled with values, but other fields might be empty." This unfortunately does not tell us whether empty means
# an empty string or null. It's also unclear whether keys may be missing. For now we assume all keys are always
# present and missing values are empty strings.


class TrivyJSONVulnerability(TypedDict):
    """Trivy JSON for one vulnerability."""

    VulnerabilityID: str
    Title: str
    Description: str
    Severity: str
    PkgName: str
    InstalledVersion: str
    FixedVersion: str
    References: list[str]


class TrivyJSONDependencyRepository(TypedDict):
    """Trivy JSON for one dependency repository."""

    Target: str
    Vulnerabilities: list[TrivyJSONVulnerability] | None  # The examples in the Trivy docs show this key can be null


TrivyJSON = list[TrivyJSONDependencyRepository]


class TrivyJSONSecurityWarnings(JSONFileSourceCollector):
    """Trivy JSON collector for security warnings."""

    def _parse_json(self, json: JSON, filename: str) -> Entities:
        """Override to parse the vulnerabilities from the Trivy JSON."""
        entities = Entities()
        for dependency_repository in cast(TrivyJSON, json):
            target = dependency_repository["Target"]
            for vulnerability in dependency_repository.get("Vulnerabilities") or []:
                vulnerability_id = vulnerability["VulnerabilityID"]
                package_name = vulnerability["PkgName"]
                entities.append(
                    Entity(
                        key=f"{vulnerability_id}@{package_name}@{target}",
                        vulnerability_id=vulnerability_id,
                        title=vulnerability["Title"],
                        description=vulnerability["Description"],
                        level=vulnerability["Severity"],
                        package_name=package_name,
                        installed_version=vulnerability["InstalledVersion"],
                        fixed_version=vulnerability["FixedVersion"],
                        url=vulnerability["References"][0],  # Assume the 1st link is at least as relevant as the others
                    ),
                )
        return entities

    def _include_entity(self, entity: Entity) -> bool:
        """Return whether to include the entity in the measurement."""
        levels = self._parameter("levels")
        return entity["level"].lower() in levels
