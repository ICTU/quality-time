"""Axe CSV accessibility violations collector."""

import csv
import re
from io import StringIO

from shared.utils.functions import md5_hash

from base_collectors import CSVFileSourceCollector
from collector_utilities.type import URL
from model import Entities, Entity, SourceResponses
from source_collectors.axe_core.violations import AxeViolationsCollector


class AxeCSVViolations(CSVFileSourceCollector, AxeViolationsCollector):
    """Collector class to get accessibility violations."""

    def _include_entity(self, entity: Entity) -> bool:
        """Return whether to include the violation."""
        return self._include_entity_based_on_impact(entity) and self._include_entity_based_on_element_filter(entity)

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Override to parse the CSV and create the entities."""
        entity_attributes = []
        for row in await self.__parse_csv(responses):
            url = self._stable_url(URL(row["URL"]))
            entity_attributes.append(
                {
                    "url": str(url),
                    "violation_type": row["Violation Type"],
                    "impact": row["Impact"],
                    "element": row["DOM Element"],
                    "page": re.sub(r"https?://[^/]+", "", str(url)),
                    "description": row["Messages"],
                    "help": row["Help"],
                }
            )
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
