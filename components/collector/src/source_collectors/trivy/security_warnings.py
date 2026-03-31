"""Trivy JSON collector."""

from typing import TYPE_CHECKING, cast

from base_collectors import JSONFileSourceCollector, SecurityWarningsSourceCollector
from model import Entities, Entity

from .json_types import TrivyJSON

if TYPE_CHECKING:
    from collector_utilities.type import JSON


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
                installed_version = vulnerability["InstalledVersion"]
                references = vulnerability.get("References", [])
                url = references[0] if references else ""  # Assume the 1st link is at least as relevant as the others
                entities.append(
                    Entity(
                        key=f"{vulnerability_id}@{package_name}@{installed_version}",
                        old_key=f"{vulnerability_id}@{package_name}@{target}",  # Key changed after v5.50.0 due to https://github.com/ICTU/quality-time/issues/12746
                        vulnerability_id=vulnerability_id,
                        title=vulnerability.get("Title", vulnerability_id),
                        description=vulnerability.get("Description", ""),
                        level=vulnerability["Severity"],
                        package_name=package_name,
                        installed_version=installed_version,
                        fixed_version=vulnerability.get("FixedVersion", ""),
                        url=url,
                    ),
                )
        return entities
