"""Jira source."""

from shared_data_model.meta.base import StrEnum
from shared_data_model.meta.entity import Color, EntityAttributeType
from shared_data_model.meta.source import Source
from shared_data_model.meta.unit import Unit
from shared_data_model.parameters import (
    Days,
    IntegerParameter,
    SingleChoiceParameter,
    StringParameter,
    TestResult,
    access_parameters,
)


class VelocityType(StrEnum):
    """Velocity types Jira can report."""

    COMMITTED = "committed points"
    COMPLETED = "completed points"
    DIFFERENCE = "completed points minus committed points"


ISSUE_ATTRIBUTES = [
    {"name": "Key", "key": "issue_key", "url": "url"},
    {"name": "Summary"},
    {"name": "Issue type", "key": "type"},
    {"name": "Status"},
    {"name": "Priority"},
    {"name": "Sprint(s)", "key": "sprint"},
    {"name": "Created", "type": EntityAttributeType.DATETIME},
    {"name": "Updated", "type": EntityAttributeType.DATETIME},
]

ALL_JIRA_METRICS = [
    "average_issue_lead_time",
    "issues",
    "manual_test_duration",
    "manual_test_execution",
    "source_version",
    "test_cases",
    "user_story_points",
    "velocity",
]

CUSTOM_FIELD_ID_HELP_URL = "https://confluence.atlassian.com/jirakb/how-to-find-id-for-custom-field-s-744522503.html"

TEST_CASE = "test_case"

JIRA = Source(
    name="Jira",
    description="Jira is a proprietary issue tracker developed by Atlassian supporting bug tracking and agile project "
    "management.",
    url="https://www.atlassian.com/software/jira",
    issue_tracker=True,
    parameters=dict(
        board=StringParameter(
            name="Board (name or id)",
            short_name="board",
            help_url="https://support.atlassian.com/jira-software-cloud/docs/what-is-a-jira-software-board/",
            mandatory=True,
            metrics=["velocity"],
        ),
        jql=StringParameter(
            name="Issue query in JQL (Jira Query Language)",
            short_name="issue query",
            mandatory=True,
            help_url="https://support.atlassian.com/jira-software-cloud/docs/"
            "use-advanced-search-with-jira-query-language-jql/",
            metrics=[
                "average_issue_lead_time",
                "issues",
                "manual_test_duration",
                "manual_test_execution",
                "test_cases",
                "user_story_points",
            ],
        ),
        lookback_days=Days(
            name="Number of days to look back in selecting issues to consider",
            short_name="number of days to look back",
            default_value="90",
            metrics=["average_issue_lead_time"],
        ),
        manual_test_duration_field=StringParameter(
            name="Manual test duration field (name or id)",
            short_name="manual test duration field",
            help_url=CUSTOM_FIELD_ID_HELP_URL,
            mandatory=True,
            metrics=["manual_test_duration"],
        ),
        manual_test_execution_frequency_field=StringParameter(
            name="Manual test execution frequency field (name or id)",
            short_name="manual test execution frequency field",
            help_url=CUSTOM_FIELD_ID_HELP_URL,
            metrics=["manual_test_execution"],
        ),
        manual_test_execution_frequency_default=Days(
            name="Default expected manual test execution frequency (days)",
            short_name="default expected manual test execution frequency",
            help="Specify how often the manual tests should be executed. For example, if the sprint length is three "
            "weeks, manual tests should be executed at least once every 21 days.",
            mandatory=True,
            default_value="21",
            metrics=["manual_test_execution"],
        ),
        story_points_field=StringParameter(
            name="Story points field (name or id)",
            short_name="story points field",
            help_url=CUSTOM_FIELD_ID_HELP_URL,
            mandatory=True,
            default_value="Story Points",
            metrics=["user_story_points"],
        ),
        test_result=TestResult(metrics=["test_cases"], values=["errored", "failed", "passed", "skipped", "untested"]),
        velocity_sprints=IntegerParameter(
            name="Number of sprints to base velocity on",
            short_name="number of sprints",
            mandatory=True,
            unit=Unit.SPRINTS,
            min_value="1",
            default_value="3",
            metrics=["velocity"],
        ),
        velocity_type=SingleChoiceParameter(
            name="Type of velocity",
            short_name="velocity type",
            help="Whether to report the number of story points committed to, the number of story points actually "
            "completed, or the difference between the two.",
            mandatory=True,
            default_value=VelocityType.COMPLETED,
            values=[VelocityType.COMMITTED, VelocityType.COMPLETED, VelocityType.DIFFERENCE],
            api_values={
                VelocityType.COMMITTED: "estimated",
                VelocityType.COMPLETED: "completed",
                VelocityType.DIFFERENCE: "difference",
            },
            metrics=["velocity"],
        ),
        **access_parameters(
            ALL_JIRA_METRICS,
            kwargs={
                "url": {
                    "help": "URL of the Jira instance, with port if necessary. For example, 'https://jira.example.org'.",
                },
                "private_token": {
                    "help_url": "https://confluence.atlassian.com/enterprise/using-personal-access-tokens-1026032365.html",
                    "validation_path": "rest/api/2/myself",
                },
            },
            include={"landing_url": False},
        ),
    ),
    entities={
        "average_issue_lead_time": {
            "name": "issue",
            "attributes": [
                *ISSUE_ATTRIBUTES,
                {"name": "Issue lead time in days", "key": "lead_time", "type": EntityAttributeType.INTEGER},
            ],
        },
        "issues": {"name": "issue", "attributes": ISSUE_ATTRIBUTES},
        "manual_test_duration": {
            "name": TEST_CASE,
            "measured_attribute": "duration",
            "attributes": [
                {"name": "Key", "key": "issue_key", "url": "url"},
                {"name": "Summary"},
                {"name": "Duration (minutes)", "key": "duration", "type": EntityAttributeType.INTEGER},
            ],
        },
        "manual_test_execution": {
            "name": TEST_CASE,
            "attributes": [
                {"name": "Key", "key": "issue_key", "url": "url"},
                {"name": "Summary"},
                {"name": "Date of last test", "key": "last_test_date", "type": EntityAttributeType.DATE},
                {
                    "name": "Desired test frequency (days)",
                    "key": "desired_test_frequency",
                    "type": EntityAttributeType.INTEGER,
                },
            ],
        },
        "test_cases": {
            "name": TEST_CASE,
            "attributes": [
                {"name": "Key", "key": "issue_key", "url": "url"},
                {"name": "Summary"},
                {"name": "Issue type", "key": "type"},
                {"name": "Status"},
                {"name": "Priority"},
                {
                    "name": "Test result",
                    "color": {
                        "errored": Color.NEGATIVE,
                        "failed": Color.NEGATIVE,
                        "passed": Color.POSITIVE,
                        "skipped": Color.WARNING,
                        "untested": Color.ACTIVE,
                    },
                },
                {"name": "Created", "type": EntityAttributeType.DATETIME},
                {"name": "Updated", "type": EntityAttributeType.DATETIME},
            ],
        },
        "user_story_points": {
            "name": "user story",
            "name_plural": "user stories",
            "measured_attribute": "points",
            "attributes": [*ISSUE_ATTRIBUTES, {"name": "Points", "type": EntityAttributeType.FLOAT}],
        },
        "velocity": {
            "name": "sprint",
            "measured_attribute": "points_measured",
            "attributes": [
                {"name": "Sprint name", "key": "name", "url": "url"},
                {"name": "Sprint goal", "key": "goal"},
                {"name": "Points committed", "type": EntityAttributeType.FLOAT},
                {"name": "Points completed", "type": EntityAttributeType.FLOAT},
                {
                    "name": "Points completed minus committed",
                    "key": "points_difference",
                    "type": EntityAttributeType.FLOAT,
                },
                {"name": "Points measured", "type": EntityAttributeType.FLOAT, "visible": False},
            ],
        },
    },
)
