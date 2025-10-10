"""Cargo audit security warnings collector."""

from typing import Literal, TypedDict, cast

from base_collectors import JSONFileSourceCollector, SecurityWarningsSourceCollector
from collector_utilities.type import JSON
from model import Entities, Entity


class Advisory(TypedDict):
    """A Cargo audit advisory."""

    id: str
    title: str
    url: str
    aliases: list[str]


class Package(TypedDict):
    """A Cargo audit package description."""

    name: str
    version: str


class CargoAuditVulnerability(TypedDict):
    """A Cargo audit vulnerability."""

    advisory: Advisory
    package: Package
    versions: dict[Literal["patched"], list[str]]


CargoAuditWarningKind = Literal["unsound", "yanked"]


class CargoAuditWarning(TypedDict):
    """A Cargo audit warning."""

    advisory: Advisory | None
    package: Package
    versions: dict[Literal["patched"], list[str]] | None
    kind: CargoAuditWarningKind


class CargoAuditJSON(TypedDict):
    """Cargo audit JSON."""

    vulnerabilities: dict[Literal["list"], list[CargoAuditVulnerability]]
    warnings: dict[CargoAuditWarningKind, list[CargoAuditWarning]]


class CargoAuditSecurityWarnings(SecurityWarningsSourceCollector, JSONFileSourceCollector):
    """Cargo Audit collector for security warnings."""

    SEVERITY_PARAMETER = "warning_types"
    ENTITY_SEVERITY_ATTRIBUTE = "warning_type"
    ENTITY_FIX_AVAILABILITY_ATTRIBUTE = "versions_patched"

    def _parse_json(self, json: JSON, filename: str) -> Entities:
        """Override to parse the security warnings from the JSON."""
        entities = Entities()
        for finding in self.__audit_findings(json):
            package_name = finding["package"]["name"]
            package_version = finding["package"]["version"]
            # Advisory can be None if a package is yanked:
            advisory = finding["advisory"] or Advisory(id="", title="", url="", aliases=[])
            versions = finding["versions"] or {}  # Versions can be None if a package is yanked
            advisory_id = advisory["id"]
            cves = [alias for alias in advisory.get("aliases", []) if alias.startswith("CVE-")]
            optional_args = {"uuid": cves[0]} if cves else {}
            entities.append(
                Entity(
                    key=f"{package_name}:{package_version}:{advisory_id}",
                    package_name=package_name,
                    package_version=package_version,
                    advisory_id=advisory_id,
                    advisory_title=advisory["title"],
                    advisory_url=advisory["url"],
                    versions_patched=", ".join(versions.get("patched", [])),
                    warning_type=finding.get("kind", "vulnerability"),
                    **optional_args,
                ),
            )
        return entities

    def __audit_findings(self, json: JSON) -> list[CargoAuditVulnerability | CargoAuditWarning]:
        """Collect all Cargo audit findings into one list for easier processing."""
        json_dict = cast(CargoAuditJSON, json)
        findings: list[CargoAuditVulnerability | CargoAuditWarning] = []
        findings.extend(json_dict["vulnerabilities"]["list"])
        for warnings_list in json_dict["warnings"].values():
            findings.extend(warnings_list)
        return findings
