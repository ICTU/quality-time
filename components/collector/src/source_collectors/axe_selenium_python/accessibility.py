"""axe-selenium-python accessibility analysis collectors."""

from collections.abc import Collection

from base_collectors import JSONFileSourceCollector
from collector_utilities.functions import md5_hash, match_string_or_regular_expression
from source_model import Entity, SourceMeasurement, SourceResponses


class AxeSeleniumPythonAccessibility(JSONFileSourceCollector):
    """Collector class to get accessibility violations."""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        """Override to parse the violations."""
        entity_attributes = []
        for response in responses:
            json = await response.json(content_type=None)
            url = json["url"]
            for violation in json.get("violations", []):
                for node in violation.get("nodes", []):
                    tags = violation.get("tags", [])
                    impact = node.get("impact")
                    if self.__include_violation(impact, tags):
                        entity_attributes.append(
                            dict(
                                description=violation.get("description"),
                                element=node.get("html"),
                                help=violation.get("helpUrl"),
                                impact=impact,
                                page=url,
                                url=url,
                                tags=", ".join(sorted(tags)),
                                violation_type=violation.get("id"),
                            )
                        )
        entities = [Entity(key=self.__create_key(attributes), **attributes) for attributes in entity_attributes]
        return SourceMeasurement(entities=entities)

    def __include_violation(self, impact: str, tags: Collection[str]) -> bool:
        """Return whether to include the violation."""
        if impact not in self._parameter("impact"):
            return False
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

    @staticmethod
    def __create_key(attributes) -> str:
        """Create a key for the entity based on the attributes."""
        # We ignore tags for two reasons: 1) If the violation is the same, so should the tags be. 2) Tags were added to
        # the entities later and including them in the key would change the key for existing entities.
        return md5_hash(",".join(str(value) for key, value in attributes.items() if key != "tags"))
