"""Harbor JSON security warnings collector."""

from typing import TYPE_CHECKING, cast

from base_collectors import JSONFileSourceCollector, SecurityWarningsSourceCollector
from model import Entities, Entity

from .json_types import REPORT_MIME_TYPE, HarborJSON

if TYPE_CHECKING:
    from collector_utilities.type import JSON


class HarborJSONSecurityWarnings(SecurityWarningsSourceCollector, JSONFileSourceCollector):
    """Harbor JSON collector for security warnings."""

    MAKE_ENTITY_SEVERITY_VALUE_LOWER_CASE = True
    ENTITY_FIX_AVAILABILITY_ATTRIBUTE = "fix_version"

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
