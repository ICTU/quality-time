"""Jira manual test duration collector."""

from .field_sum_base import JiraFieldSumBase


class JiraManualTestDuration(JiraFieldSumBase):
    """Collector to get manual test duration from Jira."""

    field_parameter = "manual_test_duration_field"
    entity_key = "duration"
