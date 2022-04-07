"""Jira user story points collector."""

from .field_sum_base import JiraFieldSumBase


class JiraUserStoryPoints(JiraFieldSumBase):
    """Collector to get user story points from Jira."""

    field_parameter = "story_points_field"
    entity_key = "points"
