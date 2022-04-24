"""SARIF JSON security warnings collector."""

from typing import cast

from base_collectors import JSONFileSourceCollector
from collector_utilities.type import JSON, JSONDict
from model import Entities, Entity


class SARIFJSONSecurityWarnings(JSONFileSourceCollector):
    """SARIF collector for security warnings."""

    def _parse_json(self, json: JSON, filename: str) -> Entities:
        """Override to parse the security warnings from the JSON."""
        entities = Entities()
        runs = cast(JSONDict, json).get("runs", [])
        for run in runs:
            rules = run["tool"]["driver"]["rules"]
            for rule in rules:
                entities.append(
                    Entity(
                        key=rule["id"],
                        title=rule["shortDescription"]["text"],
                        description=rule["fullDescription"]["text"],
                    )
                )
        return entities
