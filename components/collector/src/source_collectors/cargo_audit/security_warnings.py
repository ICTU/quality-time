"""Cargo Audit security warnings collector."""

from typing import cast

from base_collectors import JSONFileSourceCollector
from collector_utilities.type import JSON, JSONDict
from model import Entities, Entity


class CargoAuditSecurityWarnings(JSONFileSourceCollector):
    """Cargo Audit collector for security warnings."""

    def _parse_json(self, json: JSON, filename: str) -> Entities:
        """Override to parse the security warnings from the JSON."""
        entities = Entities()
        vulnerabilities = cast(JSONDict, json).get("vulnerabilities", {}).get("list", [])
        for vulnerability in vulnerabilities:
            package_name = vulnerability["package"]["name"]
            package_version = vulnerability["package"]["version"]
            advisory_id = vulnerability["advisory"]["id"]
            entities.append(
                Entity(
                    key=f"{package_name}:{package_version}:{advisory_id}",
                    package_name=package_name,
                    package_version=package_version,
                    advisory_id=advisory_id,
                    advisory_title=vulnerability["advisory"]["title"],
                    advisory_url=vulnerability["advisory"]["url"],
                    versions_patched=", ".join(vulnerability.get("versions", {}).get("patched", [])),
                ),
            )
        return entities
