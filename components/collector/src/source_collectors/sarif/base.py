"""SARIF JSON collector."""

from typing import cast

from base_collectors import JSONFileSourceCollector
from collector_utilities.type import JSON, JSONDict
from model import Entities, Entity


class SARIFJSONBase(JSONFileSourceCollector):
    """Base class for collectors that read SARIF JSON files."""

    def _parse_json(self, json: JSON, filename: str) -> Entities:
        """Override to parse the analysis results from the SARIF JSON."""
        entities = Entities()
        runs = cast(JSONDict, json).get("runs", [])
        for run in runs:
            rules = run["tool"]["driver"]["rules"]
            for result in run["results"]:
                rule = self._lookup_violated_rule(result, rules)
                locations = [
                    location["physicalLocation"]["artifactLocation"]["uri"] for location in result["locations"]
                ]
                entities.append(
                    Entity(
                        key=f'{rule["id"]}@{",".join(locations)}',
                        message=result["message"]["text"],
                        level=result["level"],
                        locations=", ".join(locations),
                        rule=rule["shortDescription"]["text"],
                        description=rule["fullDescription"]["text"],
                        url=rule.get("helpUri", ""),
                    ),
                )
        return entities

    @staticmethod
    def _lookup_violated_rule(result: dict, rules: list[dict]) -> dict:
        """Return the rule that was violated, using either the 'ruleIndex' or 'ruleId' reference."""
        if "ruleId" in result:
            return next(filter(lambda rule: rule["id"] == result["ruleId"], rules))
        return cast(dict, rules[result["ruleIndex"]])

    def _include_entity(self, entity: Entity) -> bool:
        """Return whether to include the entity in the measurement."""
        levels = self._parameter("levels")
        return entity["level"] in levels
