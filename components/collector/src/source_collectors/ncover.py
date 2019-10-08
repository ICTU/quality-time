"""NCover collectors."""

import re
from abc import ABC
from typing import Tuple

from bs4 import BeautifulSoup, Tag
from dateutil.parser import parse

from utilities.functions import days_ago
from utilities.type import Responses, Value
from .source_collector import SourceCollector


class NCoverBase(SourceCollector, ABC):  # pylint: disable=abstract-method
    """Base class for NCover collectors."""

    @staticmethod
    def _execution_summary(responses: Responses) -> Tag:
        """Return the execution summary part of the NCover report."""
        return BeautifulSoup(responses[0].text, "html.parser").find("div", id="execution_summary")


class NCoverCoverageBase(NCoverBase, ABC):  # pylint: disable=abstract-method
    """Base class for NCover coverage collectors."""

    coverage_label = "Subclass responsibility"

    def _parse_source_responses_value(self, responses: Responses) -> Value:
        covered_items, total_items = self.__coverage(responses)
        return str(int(total_items) - int(covered_items))

    def _parse_source_responses_total(self, responses: Responses) -> Value:
        return self.__coverage(responses)[1]

    def __coverage(self, responses) -> Tuple[str, str]:
        """Return the coverage (covered items, total number) from the execution summary with the specified label."""
        execution_summary = self._execution_summary(responses)
        label_div = execution_summary.find("div", class_="label", string=f"{self.coverage_label}:")
        value_div = label_div.find_next_sibling("div")
        coverage_div = value_div.find("div", string=re.compile(r"\(\d+ of \d+\)"))
        coverage_parts = str(coverage_div.string)[1:-1].split(" of ")
        return coverage_parts[0], coverage_parts[1]


class NCoverUncoveredLines(NCoverCoverageBase):
    """Collector to get the uncovered lines. Since NCover doesn't report lines, but sequence points, we use those.
    See http://www.ncover.com/blog/code-coverage-metrics-sequence-point-coverage/."""

    coverage_label = "Sequence Points"


class NCoverUncoveredBranches(NCoverCoverageBase):
    """Collector to get the uncovered branches."""

    coverage_label = "Branches"


class NCoverSourceUpToDateness(NCoverBase):
    """Collector to collect the NCover report age."""

    def _parse_source_responses_value(self, responses: Responses) -> Value:
        execution_summary = self._execution_summary(responses)
        collection_date = execution_summary.find("div", class_="value")
        return str(days_ago(parse(collection_date.string)))
