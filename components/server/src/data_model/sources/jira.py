"""Jira source."""

from enum import Enum

from ..meta.entity import EntityAttributeType
from ..meta.source import Source
from ..meta.unit import Unit
from ..parameters import access_parameters, Days, IntegerParameter, SingleChoiceParameter, StringParameter


class VelocityType(str, Enum):
    """Velocity types Jira can report."""

    COMMITTED = "committed points"
    COMPLETED = "completed points"
    DIFFERENCE = "completed points minus committed points"


ISSUE_ATTRIBUTES = [
    dict(name="Key", key="issue_key", url="url"),
    dict(name="Summary"),
    dict(name="Issue type", key="type"),
    dict(name="Status"),
    dict(name="Priority"),
    dict(name="Sprint(s)", key="sprint"),
    dict(name="Created", type=EntityAttributeType.DATETIME),
    dict(name="Updated", type=EntityAttributeType.DATETIME),
]

ALL_JIRA_METRICS = [
    "issues",
    "manual_test_duration",
    "manual_test_execution",
    "source_version",
    "user_story_points",
    "velocity",
]

CUSTOM_FIELD_ID_HELP_URL = "https://confluence.atlassian.com/jirakb/how-to-find-id-for-custom-field-s-744522503.html"

JIRA = Source(
    name="Jira",
    description="Jira is a proprietary issue tracker developed by Atlassian supporting bug tracking and agile project "
    "management.",
    url="https://www.atlassian.com/software/jira",
    parameters=dict(
        jql=StringParameter(
            name="Issue query in JQL (Jira Query Language)",
            short_name="issue query",
            mandatory=True,
            help_url="https://support.atlassian.com/jira-software-cloud/docs/"
            "use-advanced-search-with-jira-query-language-jql/",
            metrics=[
                "issues",
                "manual_test_duration",
                "manual_test_execution",
                "user_story_points",
            ],
        ),
        board=StringParameter(
            name="Board (name or id)",
            short_name="board",
            help_url="https://support.atlassian.com/jira-software-cloud/docs/what-is-a-jira-software-board/",
            mandatory=True,
            metrics=["velocity"],
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
            help="Whether to report the amount of story points committed to, the amount of story points actually "
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
        story_points_field=StringParameter(
            name="Story points field (name or id)",
            short_name="story points field",
            help_url=CUSTOM_FIELD_ID_HELP_URL,
            mandatory=True,
            default_value="Story Points",
            metrics=["user_story_points"],
        ),
        **access_parameters(
            ALL_JIRA_METRICS,
            kwargs=dict(
                url=dict(
                    help="URL of the Jira instance, with port if necessary. For example, 'https://jira.example.org'."
                )
            ),
            include=dict(landing_url=False, private_token=False),
        )
    ),
    entities=dict(
        issues=dict(name="issue", attributes=ISSUE_ATTRIBUTES),
        manual_test_duration=dict(
            name="test case",
            measured_attribute="duration",
            attributes=[
                dict(name="Key", key="issue_key", url="url"),
                dict(name="Summary"),
                dict(name="Duration (minutes)", key="duration", type=EntityAttributeType.INTEGER),
            ],
        ),
        manual_test_execution=dict(
            name="test case",
            attributes=[
                dict(name="Key", key="issue_key", url="url"),
                dict(name="Summary"),
                dict(name="Date of last test", key="last_test_date", type=EntityAttributeType.DATE),
                dict(
                    name="Desired test frequency (days)", key="desired_test_frequency", type=EntityAttributeType.INTEGER
                ),
            ],
        ),
        user_story_points=dict(
            name="user story",
            name_plural="user stories",
            measured_attribute="points",
            attributes=ISSUE_ATTRIBUTES + [dict(name="Points", type=EntityAttributeType.FLOAT)],
        ),
        velocity=dict(
            name="sprint",
            measured_attribute="points_measured",
            attributes=[
                dict(name="Sprint name", key="name", url="url"),
                dict(name="Sprint goal", key="goal"),
                dict(name="Points committed", type=EntityAttributeType.FLOAT),
                dict(name="Points completed", type=EntityAttributeType.FLOAT),
                dict(name="Points completed minus committed", key="points_difference", type=EntityAttributeType.FLOAT),
                dict(name="Points measured", type=EntityAttributeType.FLOAT, visible=False),
            ],
        ),
    ),
)
