"""Generic metrics security warnings collector."""

from typing import cast

from base_collectors import JSONFileSourceCollector
from collector_utilities.functions import md5_hash
from collector_utilities.type import JSON, JSONDict
from model import Entities, Entity


class GenericJSONSecurityWarnings(JSONFileSourceCollector):
    """Generic collector for security warnings."""

    def _parse_json(self, json: JSON, filename: str) -> Entities:
        """Override to parse the security warnings from the JSON."""
        entities = Entities()
        vulnerabilities = cast(JSONDict, json).get("vulnerabilities", [])
        for vulnerability in vulnerabilities:
            key = md5_hash(f'{vulnerability["title"]}:{vulnerability["description"]}')
            entities.append(
                Entity(
                    key=key,
                    title=vulnerability["title"],
                    description=vulnerability["description"],
                    severity=vulnerability["severity"],
                )
            )
        return entities
