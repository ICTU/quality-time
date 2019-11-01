"""Axe accessibility analysis metric source."""

import csv
import hashlib
import re
from io import StringIO
from typing import Dict, List, Tuple

from collector_utilities.type import Responses, Value, Entities
from .source_collector import FileSourceCollector


class AxeCSVAccessibility(FileSourceCollector):
    """Collector class to get accessibility violations."""

    file_extensions = ["csv"]

    def _parse_source_responses_value(self, responses: Responses) -> Value:
        """Simply count the rows in the csv file."""
        return str(len(list(self.__parse_csv(responses))))

    def _parse_source_responses_entities(self, responses: Responses) -> Entities:
        """Convert csv rows of the Axe report into entities, in this case accessibility violations."""
        return [
            dict(
                key=hashlib.md5(row.strip().encode('utf-8')).hexdigest(),  # nosec
                violation_type=parsed_row["Violation Type"], impact=parsed_row["Impact"], url=str(parsed_row["URL"]),
                element=parsed_row["DOM Element"], page=re.sub(r'http[s]?://[^/]+', '', parsed_row['URL']),
                description=parsed_row["Messages"], help=parsed_row["Help"])
            for row, parsed_row in self.__parse_csv(responses)]

    def __parse_csv(self, responses: Responses) -> List[Tuple[str, Dict[str, str]]]:
        """Parse the CSV and return the rows and parsed items ."""
        impact_levels = self._parameter("impact")
        violation_types = self._parameter("violation_type")
        rows, parsed_rows = [], []
        for response in responses:
            csv_text = response.text.strip()
            rows.extend(csv_text.split("\n")[1:])
            parsed_rows.extend(list(csv.DictReader(StringIO(csv_text))))
        return [
            (row, parsed_row) for (row, parsed_row) in zip(rows, parsed_rows)
            if parsed_row["Impact"] in impact_levels and parsed_row["Violation Type"] in violation_types]
