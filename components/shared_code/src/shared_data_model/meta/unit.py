"""Metric and parameter units."""

from enum import StrEnum, auto


class Unit(StrEnum):
    """Supported units."""

    BLOCK = auto()
    BLOCKS = auto()
    BRANCH = auto()
    BRANCHES = auto()
    CI_JOB = "CI-job"
    CI_JOBS = "CI-jobs"
    CI_JOB_RUN = "CI-job run"
    CI_JOB_RUNS = "CI-job runs"
    COMPLEX_UNIT = "complex unit"
    COMPLEX_UNITS = "complex units"
    COMPLIANCE = auto()
    DAY = auto()
    DAYS = auto()
    DEPENDENCY = auto()
    DEPENDENCIES = auto()
    DOWNVOTE = auto()
    DOWNVOTES = auto()
    FAILED_DEPLOYMENT = "failed deployment"
    FAILED_DEPLOYMENTS = "failed deployments"
    ISSUE = auto()
    ISSUES = auto()
    LINE = auto()
    LINES = auto()
    LONG_UNIT = "long unit"
    LONG_UNITS = "long units"
    MANUAL_TEST_CASE = "manual test case"
    MANUAL_TEST_CASES = "manual test cases"
    MERGE_REQUEST = "merge request"
    MERGE_REQUESTS = "merge requests"
    METRIC = auto()
    METRICS = auto()
    MINUTE = auto()
    MINUTES = auto()
    MISSING_METRIC = "missing metric"
    MISSING_METRICS = "missing metrics"
    NONE = ""
    SECURITY_WARNING = "security warning"
    SECURITY_WARNINGS = "security warnings"
    SPRINT = auto()
    SPRINTS = auto()
    SUPPRESSED_VIOLATION = "suppressed violation"
    SUPPRESSED_VIOLATIONS = "suppressed violations"
    TEST = auto()
    TESTS = auto()
    TEST_CASE = "test case"
    TEST_CASES = "test cases"
    TEST_SUITE = "test suite"
    TEST_SUITES = "test suites"
    TODO_OR_FIXME_COMMENT = "todo or fixme comment"
    TODO_AND_FIXME_COMMENTS = "todo and fixme comments"
    TRANSACTION = auto()
    TRANSACTIONS = auto()
    UNCOVERED_BRANCH = "uncovered branch"
    UNCOVERED_BRANCHES = "uncovered branches"
    UNCOVERED_LINE = "uncovered line"
    UNCOVERED_LINES = "uncovered lines"
    UNIT_WITH_TOO_MANY_PARAMETERS = "unit with too many parameters"
    UNITS_WITH_TOO_MANY_PARAMETERS = "units with too many parameters"
    UPVOTE = auto()
    UPVOTES = auto()
    USER_STORY_POINT = "user story point"
    USER_STORY_POINTS = "user story points"
    USER_STORY_POINT_PER_SPRINT = "user story point per sprint"
    USER_STORY_POINTS_PER_SPRINT = "user story points per sprint"
    VIOLATION = auto()
    VIOLATIONS = auto()
    VIRTUAL_USER = "virtual user"
    VIRTUAL_USERS = "virtual users"
