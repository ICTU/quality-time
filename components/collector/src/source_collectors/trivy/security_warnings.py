"""Trivy JSON collector."""

from typing import TypedDict, cast

from base_collectors import JSONFileSourceCollector, SecurityWarningsSourceCollector
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


class TrivyJSONResult(TypedDict):
    """Trivy JSON for one dependency repository."""

    Target: str
    Vulnerabilities: list[TrivyJSONVulnerability] | None  # The examples in the Trivy docs show this key can be null


# Trivy JSON reports come in two different forms, following schema version 1 or schema version 2.
# Schema version 1 is not explicitly documented as a schema. The Trivy docs only give an example report.
# See https://aquasecurity.github.io/trivy/v0.55/docs/configuration/reporting/#json.
# Schema version 2 is not explicitly documented as a schema either. The only thing available seems to be a GitHub
# discussion: https://github.com/aquasecurity/trivy/discussions/1050.
# Issue to improve the documentation: https://github.com/aquasecurity/trivy/discussions/7552

TriviJSONSchemaVersion1 = list[TrivyJSONResult]


class TrivyJSONSchemaVersion2(TypedDict):
    """Trivy JSON conform schema version 2."""

    SchemaVersion: int
    Results: list[TrivyJSONResult]


TrivyJSON = TriviJSONSchemaVersion1 | TrivyJSONSchemaVersion2


class TrivyJSONSecurityWarnings(SecurityWarningsSourceCollector, JSONFileSourceCollector):
    """Trivy JSON collector for security warnings."""

    SEVERITY_PARAMETER = "levels"
    ENTITY_SEVERITY_ATTRIBUTE = "level"
    MAKE_ENTITY_SEVERITY_VALUE_LOWER_CASE = True
    ENTITY_FIX_AVAILABILITY_ATTRIBUTE = "fixed_version"

    def _parse_json(self, json: JSON, filename: str) -> Entities:
        """Override to parse the vulnerabilities from the Trivy JSON."""
        entities = Entities()
        trivy_json = cast(TrivyJSON, json)
        results = trivy_json["Results"] if isinstance(trivy_json, dict) else trivy_json
        for result in results:
            target = result["Target"]
            for vulnerability in result.get("Vulnerabilities") or []:
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
