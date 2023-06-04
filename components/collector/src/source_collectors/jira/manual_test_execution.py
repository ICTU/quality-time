"""Jira manual test execution collector."""

from datetime import datetime

from collector_utilities.date_time import days_ago, now, parse_datetime
from collector_utilities.type import URL
from model import Entity

from .issues import JiraIssues


class JiraManualTestExecution(JiraIssues):
    """Collector for the number of manual test cases that have not been executed recently enough."""

    def _create_entity(self, issue: dict, url: URL) -> Entity:
        """Extend to also add the test information to the issue entity."""
        entity = super()._create_entity(issue, url)
        entity["last_test_date"] = str(self.__last_test_datetime(issue).date())
        entity["desired_test_frequency"] = str(self.__desired_test_execution_frequency(issue))
        return entity

    def _include_issue(self, issue: dict) -> bool:
        """Override to only include tests/issues that have been tested too long ago."""
        return days_ago(self.__last_test_datetime(issue)) > self.__desired_test_execution_frequency(issue)

    def _fields(self) -> str:
        """Extend to also get the issue comments so we can get the date of the most recent comment."""
        return super()._fields() + ",comment"

    @staticmethod
    def __last_test_datetime(issue: dict) -> datetime:
        """Return the datetime of the last test."""
        comment_dates = [comment["updated"] for comment in issue["fields"]["comment"]["comments"]]
        return parse_datetime(max(comment_dates)) if comment_dates else now()

    def __desired_test_execution_frequency(self, issue: dict) -> int:
        """Return the desired test frequency for this issue."""
        frequency = issue["fields"].get(self._parameter("manual_test_execution_frequency_field"))
        return int(
            round(float(frequency)) if frequency else str(self._parameter("manual_test_execution_frequency_default")),
        )
