"""Axe HTML reporter accessibility collector."""

from typing import Iterator

from bs4 import Tag

from base_collectors import HTMLFileSourceCollector
from collector_utilities.functions import md5_hash
from model import Entities, Entity, SourceResponses

from ..axe_core.accessibility import AxeAccessibilityCollector


class AxeHTMLReporterAccessibility(HTMLFileSourceCollector, AxeAccessibilityCollector):
    """Collector class to get accessibility violations."""

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Override to parse the violations."""
        entity_attributes: list[dict[str, str]] = []
        for response in responses:
            entity_attributes.extend(self.__parse_html_soup(await self._soup(response)))
        return Entities(Entity(key=self.__create_key(attributes), **attributes) for attributes in entity_attributes)

    def __parse_html_soup(self, soup: Tag) -> Iterator[dict[str, str]]:
        """Parse the entity attributes from the HTML."""
        page_url = soup.select_one("div.summary > a")["href"]
        for result_type in self._parameter("result_types"):
            if result_type == "violations":
                yield from self.__parse_violations_from_html_soup(soup, page_url)
            else:
                yield from self.__parse_rules_from_html_soup(soup, page_url, result_type)

    def __parse_violations_from_html_soup(self, soup: Tag, page_url: str) -> Iterator[dict[str, str]]:
        """Parse the entity attributes of violated rules from the HTML."""
        for violated_rule in soup.select("div.violationCard > div.card-body"):
            impact = violated_rule("h6")[2].get_text(strip=True)
            tags = self.__parse_tags(violated_rule)
            if not self._include_violation(impact, tags):
                continue
            violation_type = violated_rule("h6")[0].get_text(strip=True)
            description = violated_rule.select_one("p.card-text").get_text(strip=True)
            help_url = violated_rule.select_one("a.learnMore")["href"]
            for violation in violated_rule.select("div.violationNode tbody tr"):
                element = self.__parse_element(violation)
                yield dict(
                    violation_type=violation_type,
                    description=description,
                    impact=impact,
                    element=element,
                    tags=", ".join(tags),
                    help=help_url,
                    page=page_url,
                    url=page_url,
                    result_type="violations",
                )

    @staticmethod
    def __parse_rules_from_html_soup(soup: Tag, page_url: str, result_type: str) -> Iterator[dict[str, str]]:
        """Parse the entity attributes of rules from the HTML."""
        for rule in soup.select(f"div#{result_type} tr"):
            if not rule("td"):
                continue  # Skip the header row
            yield dict(
                violation_type=rule("td")[1].get_text(strip=True),
                description=rule("td")[0].get_text(strip=True),
                impact="",
                element="",
                tags="",
                help="",
                page=page_url,
                url=page_url,
                result_type=result_type,
            )

    @staticmethod
    def __parse_tags(violated_rule: Tag) -> list[str]:
        """Parse the tags from the violated rule soup."""
        tags_list = [node for node in violated_rule("h6") if "Issue Tags:" in node.get_text()]
        return sorted(tag.string.strip() for tag in tags_list[0]("span"))

    @staticmethod
    def __parse_element(violation: Tag) -> str:
        """Parse the element from the violation soup."""
        element_tags = violation("td")[1].find_all(True, recursive=False)  # Find all direct child tags
        return str(element_tags[-1].get_text("", strip=True))

    @staticmethod
    def __create_key(attributes) -> str:
        """Create a key for the entity based on the attributes."""
        return md5_hash(",".join(sorted(attributes.values())))
