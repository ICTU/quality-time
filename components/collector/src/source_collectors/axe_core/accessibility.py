"""Axe-core accessibility analysis collectors."""

from collections.abc import Generator
from typing import Any

from base_collectors import JSONFileSourceCollector, SourceCollector
from collector_utilities.functions import match_string_or_regular_expression, md5_hash
from collector_utilities.type import JSON
from model import Entities, Entity


class AxeAccessibilityCollector(SourceCollector):
    """Collector base class for getting accessibility violations from Axe."""

    def _include_entity(self, entity: Entity) -> bool:
        """Return whether to include the entity."""
        return (
            self._include_entity_based_on_impact(entity)
            and self._include_entity_based_on_tags(entity)
            and self._include_entity_based_on_element_filter(entity)
        )

    def _include_entity_based_on_impact(self, entity: Entity) -> bool:
        """Return whether to include the entity based on the impact."""
        return impact in self._parameter("impact") if (impact := entity["impact"]) else True

    def _include_entity_based_on_tags(self, entity: Entity) -> bool:
        """Return whether to include the entity based on the tags."""
        tags = entity["tags"].split(", ")
        if tags_to_include := self._parameter("tags_to_include"):
            for tag in tags:
                if match_string_or_regular_expression(tag, tags_to_include):
                    break
            else:
                return False
        if tags_to_ignore := self._parameter("tags_to_ignore"):
            for tag in tags:
                if match_string_or_regular_expression(tag, tags_to_ignore):
                    return False
        return True

    def _include_entity_based_on_element_filter(self, entity: Entity) -> bool:
        """Return whether to include the entity based on the element filters."""
        element_include_filter = self._parameter("element_include_filter")
        if element_include_filter and not match_string_or_regular_expression(entity["element"], element_include_filter):
            return False
        element_exclude_filter = self._parameter("element_exclude_filter")
        if element_exclude_filter and match_string_or_regular_expression(entity["element"], element_exclude_filter):
            return False
        return True


class AxeCoreAccessibility(JSONFileSourceCollector, AxeAccessibilityCollector):
    """Collector class to get accessibility violations from Axe-core JSON output."""

    def _parse_json(self, json: JSON, filename: str) -> Entities:
        """Override to parse the violations."""
        entity_attributes = []
        for test_result in self.__parse_test_results(json):
            violations = {result_type: test_result.get(result_type) for result_type in self._parameter("result_types")}
            url = test_result.get("url", "")
            entity_attributes.extend(self.__parse_violations(violations, url))
        return Entities(Entity(key=self.__create_key(attributes), **attributes) for attributes in entity_attributes)

    def __parse_test_results(self, json) -> Generator:
        """Yield dicts with test result (applicable/incomplete/violations/passes) as key and rules as values."""
        if isinstance(json, list):
            if json and "tags" in json[0]:
                yield {"violations": json}  # The items in the list are violated rules
            else:
                for item in json:
                    yield from self.__parse_test_results(item)  # Recursively parse the nested JSON
        else:
            yield json  # JSON is a dict with result types as keys and rules as values

    def __parse_violations(self, violations: dict[str, list[dict[str, list]]], url: str) -> list[dict[str, Any]]:
        """Parse the violations."""
        entity_attributes = []
        for result_type, violations_by_result_type in violations.items():
            for violation in violations_by_result_type:
                entity_attributes.extend(self.__parse_violation(violation, result_type, url))
        return entity_attributes

    @staticmethod
    def __parse_violation(violation: dict[str, list], result_type: str, url: str) -> list[dict[str, Any]]:
        """Parse a violation."""
        return [
            {
                "description": violation.get("description"),
                "element": node.get("html"),
                "help": violation.get("helpUrl"),
                "impact": node.get("impact"),
                "page": url,
                "url": url,
                "result_type": result_type,
                "tags": ", ".join(sorted(violation.get("tags", []))),
                "violation_type": violation.get("id"),
            }
            for node in violation.get("nodes", []) or [violation]  # Use the violation as node if it has no nodes
        ]

    @staticmethod
    def __create_key(attributes) -> str:
        """Create a key for the entity based on the attributes."""
        # We ignore tags for two reasons: 1) If the violation is the same, so should the tags be. 2) Tags were added to
        # the entities later and including them in the key would change the key for existing entities. Nr 2) also
        # applies to the result type.
        return md5_hash(",".join(str(value) for key, value in attributes.items() if key not in {"tags", "result_type"}))
