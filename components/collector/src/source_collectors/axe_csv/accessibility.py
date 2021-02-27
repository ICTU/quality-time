"""Axe CSV accessibility collector."""

import csv
import re
from io import StringIO

from base_collectors import CSVFileSourceCollector
from collector_utilities.functions import md5_hash
from source_model import Entities, Entity, SourceResponses


class AxeCSVAccessibility(CSVFileSourceCollector):
    """Collector class to get accessibility violations."""

    async def _parse_entities(self, responses: SourceResponses) -> Entities:
        """Override to parse the CSV and create the entities."""
        entity_attributes = [
            dict(
                url=str(row["URL"]),
                violation_type=row["Violation Type"],
                impact=row["Impact"],
                element=row["DOM Element"],
                page=re.sub(r"http[s]?://[^/]+", "", row["URL"]),
                description=row["Messages"],
                help=row["Help"],
            )
            for row in await self.__parse_csv(responses)
        ]
        return [
            Entity(key=md5_hash(",".join(str(value) for value in attributes.values())), **attributes)
            for attributes in entity_attributes
        ]

    async def __parse_csv(self, responses: SourceResponses) -> list[dict[str, str]]:
        """Parse the CSV and return the rows and parsed items ."""
        impact_levels = self._parameter("impact")
        violation_types = self._parameter("violation_type")
        rows = []
        for response in responses:
            csv_text = (await response.text()).strip()
            rows.extend(list(csv.DictReader(StringIO(csv_text, newline=""))))
        return [row for row in rows if row["Impact"] in impact_levels and row["Violation Type"] in violation_types]
