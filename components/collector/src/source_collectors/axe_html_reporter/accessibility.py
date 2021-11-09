"""Axe HTML reporter accessibility collector."""

from bs4 import Tag

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
            page_url = soup.select_one("div.summary > a")["href"]
            for violated_rule in soup.select("div.violationCard > div.card-body"):
                violation_type = violated_rule("h6")[0].get_text(strip=True)
                description = violated_rule.select_one("p.card-text").get_text(strip=True)
                tags = self.__parse_tags(violated_rule)
                impact = violated_rule("h6")[2].get_text(strip=True)
                help_url = violated_rule.select_one("a.learnMore")["href"]
                for violation in violated_rule.select("div.violationNode tbody tr"):
                    element = self.__parse_element(violation)
                    entity_attributes.append(
                        dict(
                            violation_type=violation_type,
                            description=description,
                            impact=impact,
                            element=element,
                            tags=tags,
                            help=help_url,
                            page=page_url,
                            url=page_url,
                        )
                    )
        return Entities(Entity(key=self.__create_key(attributes), **attributes) for attributes in entity_attributes)

    @staticmethod
    def __parse_tags(violated_rule: Tag) -> str:
        """Parse the tags from the violated rule soup."""
        tags_list = [node for node in violated_rule("h6") if "Issue Tags:" in node.get_text()]
        return ", ".join(sorted(tag.string.strip() for tag in tags_list[0]("span")))

    @staticmethod
    def __parse_element(violation: Tag) -> str:
        """Parse the element from the violation soup."""
        element_tags = violation("td")[1].find_all(True, recursive=False)  # Find all direct child tags
        return str(element_tags[-1].get_text("", strip=True))

    @staticmethod
    def __create_key(attributes) -> str:
        """Create a key for the entity based on the attributes."""
        return md5_hash(",".join(sorted(attributes.values())))
