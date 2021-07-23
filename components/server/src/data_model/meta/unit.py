"""Metric and parameter units."""

from enum import Enum


class Unit(str, Enum):
    """Supported units."""

    BLOCKS = "blocks"
    BRANCHES = "branches"
    CI_JOBS = "CI-jobs"
    COMPLEX_UNITS = "complex units"
    DAYS = "days"
    DEPENDENCIES = "dependencies"
    DOWNVOTES = "downvotes"
    ISSUES = "issues"
    LINES = "lines"
    LONG_UNITS = "long units"
    MANUAL_TEST_CASES = "manual test cases"
    MERGE_REQUESTS = "merge requests"
    METRICS = "metrics"
    MINUTES = "minutes"
    MISSING_METRICS = "missing metrics"
    NONE = ""
    SECURITY_WARNINGS = "security warnings"
    SPRINTS = "sprints"
    SUPPRESSED_VIOLATIONS = "suppressed violations"
    TEST_CASES = "test cases"
    TESTS = "tests"
    TRANSACTIONS = "transactions"
    UNCOVERED_BRANCHES = "uncovered branches"
    UNCOVERED_LINES = "uncovered lines"
    UNITS_WITH_TOO_MANY_PARAMETERS = "units with too many parameters"
    UPVOTES = "upvotes"
    USERS = "users"
    USER_STORY_POINTS = "user story points"
    USER_STORY_POINTS_PER_SPRINT = "user story points per sprint"
    VIOLATIONS = "violations"
