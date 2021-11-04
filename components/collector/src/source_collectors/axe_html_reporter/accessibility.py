"""Axe HTML reporter accessibility collector."""

from base_collectors import HTMLFileSourceCollector
from collector_utilities.functions import md5_hash
from model import Entities, Entity, SourceResponses


class AxeHTMLReporterAccessibility(HTMLFileSourceCollector):
    """Collector class to get accessibility violations."""

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Override to parse the violations."""
        entity_attributes = []
        for response in responses:
            soup = await self._soup(response)
            for violated_rule in soup.select("div.violationCard > div.card-body"):
                rule = violated_rule.select_one("h5").get_text(" ", strip=True)
                tags_list = [node for node in violated_rule("h6") if "Issue Tags:" in node.get_text()]
                tags = sorted(tag.string.strip() for tag in tags_list[0]("span"))
                for violation in violated_rule.select("div.violationNode tbody tr"):
                    element = violation("td")[1].get_text(" ", strip=True)
                    solution = violation("td")[2].get_text(" ", strip=True)
                    entity_attributes.append(dict(solution=solution, element=element, rule=rule, tags=tags))
        return Entities(Entity(key=self.__create_key(attributes), **attributes) for attributes in entity_attributes)

    @staticmethod
    def __create_key(attributes) -> str:
        """Create a key for the entity based on the attributes."""
        return md5_hash(",".join(str(value) for value in attributes.values()))
