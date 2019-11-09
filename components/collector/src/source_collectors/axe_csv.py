"""Axe accessibility analysis metric source."""

import csv
import hashlib
import re
from io import StringIO
from typing import Dict, List

from collector_utilities.type import Responses, Value, Entities, Entity
from .source_collector import FileSourceCollector


class AxeCSVAccessibility(FileSourceCollector):
    """Collector class to get accessibility violations."""

    file_extensions = ["csv"]

    def _parse_source_responses_value(self, responses: Responses) -> Value:
        """Simply count the rows in the csv file."""
        return str(len(list(self.__parse_csv(responses))))

    def _parse_source_responses_entities(self, responses: Responses) -> Entities:
        """Convert csv rows of the Axe report into entities, in this case accessibility violations."""
        entities: Entities = [
            dict(
                url=str(row["URL"]), violation_type=row["Violation Type"], impact=row["Impact"],
                element=row["DOM Element"], page=re.sub(r'http[s]?://[^/]+', '', row['URL']),
                description=row["Messages"], help=row["Help"])
            for row in self.__parse_csv(responses)]
        for entity in entities:
            entity["key"] = self.hash_entity(entity)
        return entities

    def __parse_csv(self, responses: Responses) -> List[Dict[str, str]]:
        """Parse the CSV and return the rows and parsed items ."""
        impact_levels = self._parameter("impact")
        violation_types = self._parameter("violation_type")
        rows = []
        for response in responses:
            csv_text = response.text.strip()
            rows.extend(list(csv.DictReader(StringIO(csv_text, newline=""))))
        return [row for row in rows if row["Impact"] in impact_levels and row["Violation Type"] in violation_types]

    @staticmethod
    def hash_entity(entity: Entity) -> str:
        """Return a hash of the entity."""
        return hashlib.md5(",".join([str(value) for value in entity.values()]).encode('utf-8')).hexdigest()  # nosec
