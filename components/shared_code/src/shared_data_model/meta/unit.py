"""Metric and parameter units."""

from enum import StrEnum, auto


class Unit(StrEnum):
    """Supported units."""

    BLOCKS = auto()
    BRANCHES = auto()
    CI_JOBS = "CI-jobs"
    CI_JOB_RUNS = "CI-job runs"
    COMPLEX_UNITS = "complex units"
    COMPLIANCE = auto()
    DAYS = auto()
    DEPENDENCIES = auto()
    DOWNVOTES = auto()
    FAILED_DEPLOYMENTS = "failed deployments"
    ISSUES = auto()
    LINES = auto()
    LONG_UNITS = "long units"
    MANUAL_TEST_CASES = "manual test cases"
    MERGE_REQUESTS = "merge requests"
    METRICS = auto()
    MINUTES = auto()
    MISSING_METRICS = "missing metrics"
    NONE = ""
    SECURITY_WARNINGS = "security warnings"
    SPRINTS = auto()
    SUPPRESSED_VIOLATIONS = "suppressed violations"
    TEST_CASES = "test cases"
    TEST_SUITES = "test suites"
    TESTS = auto()
    TODO_AND_FIXME_COMMENTS = "todo and fixme comments"
    TRANSACTIONS = auto()
    UNCOVERED_BRANCHES = "uncovered branches"
    UNCOVERED_LINES = "uncovered lines"
    UNITS_WITH_TOO_MANY_PARAMETERS = "units with too many parameters"
    UPVOTES = auto()
    USER_STORY_POINTS = "user story points"
    USER_STORY_POINTS_PER_SPRINT = "user story points per sprint"
    VIOLATIONS = auto()
    VIRTUAL_USERS = "virtual users"
