"""Axe accessibility analysis metric source."""

import csv
import re
from io import StringIO
from typing import Dict, List

from collector_utilities.functions import md5_hash
from collector_utilities.type import Entities
from base_collectors import CSVFileSourceCollector, SourceMeasurement, SourceResponses


class AxeCSVAccessibility(CSVFileSourceCollector):
    """Collector class to get accessibility violations."""

    async def _parse_source_responses(self, responses: SourceResponses) -> SourceMeasurement:
        entities: Entities = [
            dict(
                url=str(row["URL"]), violation_type=row["Violation Type"], impact=row["Impact"],
                element=row["DOM Element"], page=re.sub(r'http[s]?://[^/]+', '', row['URL']),
                description=row["Messages"], help=row["Help"])
            for row in await self.__parse_csv(responses)]
        for entity in entities:
            entity["key"] = md5_hash(",".join(str(value) for value in entity.values()))
        return SourceMeasurement(entities=entities)

    async def __parse_csv(self, responses: SourceResponses) -> List[Dict[str, str]]:
        """Parse the CSV and return the rows and parsed items ."""
        impact_levels = self._parameter("impact")
        violation_types = self._parameter("violation_type")
        rows = []
        for response in responses:
            csv_text = (await response.text()).strip()
            rows.extend(list(csv.DictReader(StringIO(csv_text, newline=""))))
        return [row for row in rows if row["Impact"] in impact_levels and row["Violation Type"] in violation_types]
