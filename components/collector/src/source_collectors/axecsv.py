"""Accessibility metric source."""

from typing import List

import hashlib
import re
import csv
from io import StringIO
import requests

from utilities.type import Value, Entities
from .source_collector import SourceCollector

class AxeCSV(SourceCollector):
    """Collector class to get accessibility violations."""

    def parse_source_responses_value(self, responses: List[requests.Response]) -> Value:
        """ Simply count the rows in the csv file. """
        csvfile = StringIO(responses[0].text, newline=None)
        return str(sum(1 for row in csv.DictReader(csvfile)))


    def parse_source_responses_entities(self, responses: List[requests.Response]) -> Entities:
        """ Convert csv rows og the axe report into the json dictionary. """

        return [dict(key=hashlib.md5(str(row).encode('utf-8')).hexdigest(), # nosec
                     violation_type=row["Violation Type"],
                     impact=row["Impact"], page=re.sub(r'http[s]?://[^/]+', '', row['URL']),
                     url=str(row["URL"]), element=row["DOM Element"], description=row["Messages"], help=row["Help"]
                     ) for row in csv.DictReader(StringIO(responses[0].text, newline=None))]
