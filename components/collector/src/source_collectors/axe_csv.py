"""Axe accessibility analysis metric source."""

import csv
import hashlib
import re
from io import StringIO
from typing import Dict, List, Tuple

from utilities.type import Responses, Value, Entities
from .source_collector import SourceCollector


class AxeCSVAccessibility(SourceCollector):
    """Collector class to get accessibility violations."""

    def _parse_source_responses_value(self, responses: Responses) -> Value:
        """Simply count the rows in the csv file."""
        return str(len(list(self.__parse_csv(responses))))

    def _parse_source_responses_entities(self, responses: Responses) -> Entities:
        """Convert csv rows of the Axe report into entities, in this case accessibility violations."""
        return [
            dict(
                key=hashlib.md5(row.encode('utf-8')).hexdigest(),  # nosec
                violation_type=items["Violation Type"], impact=items["Impact"], url=str(items["URL"]),
                element=items["DOM Element"], page=re.sub(r'http[s]?://[^/]+', '', items['URL']),
                description=items["Messages"], help=items["Help"])
            for row, items in self.__parse_csv(responses)]

    def __parse_csv(self, responses: Responses) -> List[Tuple[str, Dict[str, str]]]:
        """Parse the CSV and return the rows and parsed items ."""
        impact_levels = self._parameter("impact")
        rows = responses[0].text.split("\n")[1:]
        parsed_rows = csv.DictReader(StringIO(responses[0].text, newline=None))
        return [
            (row, parsed_row) for row, parsed_row in zip(rows, parsed_rows) if parsed_row["Impact"] in impact_levels]
