"""Trivy JSON collector."""

from typing import cast

from base_collectors import JSONFileSourceCollector, SecurityWarningsSourceCollector
from collector_utilities.type import JSON
from model import Entities, Entity

from .base import TrivyJSON


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
                        fixed_version=vulnerability.get("FixedVersion", ""),
                        url=vulnerability["References"][0],  # Assume the 1st link is at least as relevant as the others
                    ),
                )
        return entities
