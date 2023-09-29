"""Harbor JSON security warnings collector."""

from typing import Final, TypedDict, cast

from base_collectors import JSONFileSourceCollector
from collector_utilities.type import JSON
from model import Entities, Entity

REPORT_MIME_TYPE: Final = "application/vnd.security.vulnerability.report; version=1.1"


class Vulnerability(TypedDict):
    """A Harbor JSON vulnerability."""

    id: str
    package: str
    version: str
    fix_version: str
    severity: str
    description: str
    links: list[str]


class HarborJSONVulnerabilityReport(TypedDict):
    """A Harbor JSON vulnerability report."""

    vulnerabilities: list[Vulnerability]


HarborJSON = TypedDict(
    "HarborJSON",
    {"application/vnd.security.vulnerability.report; version=1.1": HarborJSONVulnerabilityReport},
)


class HarborJSONSecurityWarnings(JSONFileSourceCollector):
    """Harbor JSON collector for security warnings."""

    def _parse_json(self, json: JSON, filename: str) -> Entities:
        """Override to parse the vulnerabilities from the Harbor JSON."""
        entities = Entities()
        for vulnerability in cast(HarborJSON, json)[REPORT_MIME_TYPE]["vulnerabilities"]:
            vulnerability_id = vulnerability["id"]
            package = vulnerability["package"]
            version = vulnerability["version"]
            entities.append(
                Entity(
                    key=f"{vulnerability_id}@{package}@{version}",
                    vulnerability_id=vulnerability_id,
                    package=package,
                    version=version,
                    fix_version=vulnerability["fix_version"],
                    severity=vulnerability["severity"],
                    description=vulnerability["description"],
                    url=vulnerability["links"][0],  # Assume the 1st link is at least as relevant as the others
                ),
            )
        return entities

    def _include_entity(self, entity: Entity) -> bool:
        """Return whether to include the entity in the measurement."""
        severities = self._parameter("severities")
        return entity["severity"].lower() in severities
