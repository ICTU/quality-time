"""Anchore security warnings collector."""

from shared.utils.functions import md5_hash

from base_collectors import JSONFileSourceCollector, SecurityWarningsSourceCollector
from collector_utilities.type import JSON
from model import Entities, Entity


class AnchoreSecurityWarnings(JSONFileSourceCollector, SecurityWarningsSourceCollector):
    """Anchore collector for security warnings."""

    def _parse_json(self, json: JSON, filename: str) -> Entities:
        """Override to parse the Anchore security warnings."""
        vulnerabilities = json.get("vulnerabilities", []) if isinstance(json, dict) else []
        return Entities([self._create_entity(vulnerability, filename) for vulnerability in vulnerabilities])

    @staticmethod
    def _create_entity(vulnerability: dict[str, str], filename: str) -> Entity:
        """Create an entity from the vulnerability."""
        cve = vulnerability["vuln"]
        return Entity(
            # Include the filename in the hash so that it is unique even when multiple images contain the
            # same package with the same vulnerability. Don't add a colon so existing hashes stay the same
            # if the source is not a zipped report (filename is an empty string in that case).
            key=md5_hash(f"{filename}{vulnerability['vuln']}:{vulnerability['package']}"),
            cve=cve,
            uuid=cve,
            filename=filename,
            package=vulnerability["package"],
            severity=vulnerability["severity"],
            fix=vulnerability["fix"],
            url=vulnerability["url"],
        )
