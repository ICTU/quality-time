"""Axe CSV accessibility collector."""

import csv
import re
from io import StringIO

from base_collectors import CSVFileSourceCollector
from collector_utilities.functions import md5_hash, match_string_or_regular_expression
from model import Entities, Entity, SourceResponses


class AxeCSVAccessibility(CSVFileSourceCollector):
    """Collector class to get accessibility violations."""

    def _include_entity(self, entity: Entity) -> bool:
        """Return whether to include the violation."""
        impact = entity["impact"]
        if impact and impact not in self._parameter("impact"):
            return False
        if element_include_filter := self._parameter("element_include_filter"):
            if not match_string_or_regular_expression(entity["element"], element_include_filter):
                return False
        if element_exclude_filter := self._parameter("element_exclude_filter"):
            if match_string_or_regular_expression(entity["element"], element_exclude_filter):
                return False
        return True

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Override to parse the CSV and create the entities."""
        entity_attributes = [
            dict(
                url=str(row["URL"]),
                violation_type=row["Violation Type"],
                impact=row["Impact"],
                element=row["DOM Element"],
                page=re.sub(r"https?://[^/]+", "", row["URL"]),
                description=row["Messages"],
                help=row["Help"],
            )
            for row in await self.__parse_csv(responses)
        ]
        return Entities(
            Entity(key=md5_hash(",".join(str(value) for value in attributes.values())), **attributes)
            for attributes in entity_attributes
        )

    @staticmethod
    async def __parse_csv(responses: SourceResponses) -> list[dict[str, str]]:
        """Parse the CSV and return the rows and parsed items ."""
        rows = []
        for response in responses:
            csv_text = (await response.text()).strip()
            rows.extend(list(csv.DictReader(StringIO(csv_text, newline=""))))
        return rows
