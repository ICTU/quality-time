"""Azure DevOps source."""

from pydantic import HttpUrl

from shared_data_model.meta.entity import Color, Entity, EntityAttribute, EntityAttributeType
from shared_data_model.meta.source import Source
from shared_data_model.parameters import (
    URL,
    Branch,
    BranchesToIgnore,
    Days,
    FailureType,
    MergeRequestState,
    MultipleChoiceParameter,
    MultipleChoiceWithAdditionParameter,
    PrivateToken,
    StringParameter,
    TargetBranchesToInclude,
    TestResult,
    Upvotes,
)

ALL_AZURE_DEVOPS_METRICS = [
    "average_issue_lead_time",
    "failed_jobs",
    "issues",
    "job_runs_within_time_period",
    "merge_requests",
    "source_up_to_dateness",
    "tests",
    "unmerged_branches",
    "unused_jobs",
    "user_story_points",
]

ISSUE_ATTRIBUTES = [
    EntityAttribute(name="Project"),
    EntityAttribute(name="Title", url="url"),
    EntityAttribute(name="Work item type"),
    EntityAttribute(name="State"),
]

PIPELINE_ATTRIBUTES = [
    EntityAttribute(name="Pipeline", key="name", url="url"),
    EntityAttribute(
        name="Status of most recent build",
        key="build_status",
        color={
            "succeeded": Color.POSITIVE,
            "failed": Color.NEGATIVE,
            "canceled": Color.ACTIVE,
            "partiallySucceeded": Color.WARNING,
        },
    ),
    EntityAttribute(name="Date of most recent build", key="build_date", type=EntityAttributeType.DATE),
]

AZURE_DEVOPS = Source(
    name="Azure DevOps Server",
    description="Azure DevOps Server (formerly known as Team Foundation Server) by Microsoft provides source code "
    "management, reporting, requirements management, project management, automated builds, testing and "
    "release management.",
    url=HttpUrl("https://azure.microsoft.com/en-us/services/devops/server/"),
    parameters={
        "url": URL(
            name="URL including organization and project",
            help="URL of the Azure DevOps instance, with port if necessary, and with organization and project. "
            "For example: 'https://dev.azure.com/{organization}/{project}'.",
            validate_on=["private_token"],
            metrics=ALL_AZURE_DEVOPS_METRICS,
        ),
        "private_token": PrivateToken(
            help_url=HttpUrl(
                "https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/"
                "use-personal-access-tokens-to-authenticate?view=azure-devops",
            ),
            metrics=ALL_AZURE_DEVOPS_METRICS,
        ),
        "wiql": StringParameter(
            name="Issue query in WIQL (Work Item Query Language)",
            short_name="issue query",
            mandatory=False,
            help="This should only contain the WHERE clause of a WIQL query, as the selected fields are static. "
            "For example, use the following clause to hide issues marked as done: \"[System.State] <> 'Done'\". "
            "See https://docs.microsoft.com/en-us/azure/devops/boards/queries/wiql-syntax?view=azure-devops.",
            metrics=["average_issue_lead_time", "issues", "user_story_points"],
        ),
        "file_path": StringParameter(
            name="File or folder path",
            short_name="path",
            help="Use the date and time the path was last changed to determine the up-to-dateness. If no path "
            "is specified, the pipeline is used to determine the up-to-dateness.",
            placeholder="none",
            metrics=["source_up_to_dateness"],
        ),
        "repository": StringParameter(
            name="Repository (name or id)",
            short_name="repository",
            placeholder="default repository",
            metrics=["merge_requests", "source_up_to_dateness", "unmerged_branches"],
        ),
        "branch": Branch(),
        "branches_to_ignore": BranchesToIgnore(
            help_url=HttpUrl(
                "https://docs.microsoft.com/en-us/azure/devops/repos/git/manage-your-branches?view=azure-devops",
            ),
        ),
        "inactive_days": Days(
            name="Number of days since last commit after which to consider branches inactive",
            short_name="number of days since last commit",
            default_value="7",
            metrics=["unmerged_branches"],
        ),
        "inactive_job_days": Days(
            name="Number of days since last build after which to consider pipelines inactive",
            short_name="number of days since last build",
            default_value="21",
            metrics=["unused_jobs"],
        ),
        "test_result": TestResult(
            values=["incomplete", "failed", "not applicable", "passed"],
            api_values={
                "incomplete": "incompleteTests",
                "failed": "unanalyzedTests",
                "passed": "passedTests",
                "not applicable": "notApplicableTests",
            },
        ),
        "test_run_names_to_include": MultipleChoiceWithAdditionParameter(
            name="Names of test runs to include (regular expressions or test run names)",
            short_name="test run names",
            help="Limit which test runs to include by test run name.",
            placeholder="all test run names",
            metrics=["tests"],
        ),
        "test_run_states_to_include": MultipleChoiceParameter(
            name="States of the test runs to include",
            short_name="test run states",
            help="Limit which test runs to include by test run state.",
            placeholder="all test run states",
            values=["aborted", "completed", "in progress", "not started"],
            api_values={
                "aborted": "aborted",
                "completed": "completed",
                "in progress": "inProgress",
                "not started": "notStarted",
            },
            metrics=["tests"],
        ),
        "jobs_to_include": MultipleChoiceWithAdditionParameter(
            name="Pipelines to include (regular expressions or pipeline names)",
            short_name="pipelines to include",
            help="Pipelines to include can be specified by pipeline name or by regular expression. "
            "Use {folder name}/{pipeline name} for the names of pipelines in folders.",
            placeholder="all",
            metrics=["failed_jobs", "job_runs_within_time_period", "source_up_to_dateness", "unused_jobs"],
        ),
        "jobs_to_ignore": MultipleChoiceWithAdditionParameter(
            name="Pipelines to ignore (regular expressions or pipeline names)",
            short_name="pipelines to ignore",
            help="Pipelines to ignore can be specified by pipeline name or by regular expression. "
            "Use {folder name}/{pipeline name} for the names of pipelines in folders.",
            metrics=["failed_jobs", "job_runs_within_time_period", "source_up_to_dateness", "unused_jobs"],
        ),
        "lookback_days_pipeline_runs": Days(
            name="Number of days to look back for selecting pipeline runs",
            short_name="number of days to look back",
            default_value="90",
            metrics=["job_runs_within_time_period"],
        ),
        "lookback_days_issues": Days(
            name="Number of days to look back for work items",
            help="Work items are selected if they are completed and have been updated within the number of days "
            "configured.",
            short_name="number of days to look back",
            default_value="90",
            metrics=["average_issue_lead_time"],
        ),
        "failure_type": FailureType(
            values=["canceled", "failed", "no result", "partially succeeded"],
            api_values={"no result": "none", "partially succeeded": "partiallySucceeded"},
        ),
        "merge_request_state": MergeRequestState(
            values=["abandoned", "active", "completed", "not set"],
            api_values={"not set": "notSet"},
        ),
        "upvotes": Upvotes(),
        "target_branches_to_include": TargetBranchesToInclude(
            help_url=HttpUrl(
                "https://docs.microsoft.com/en-us/azure/devops/repos/git/manage-your-branches?view=azure-devops",
            ),
        ),
    },
    entities={
        "average_issue_lead_time": Entity(
            name="work item",
            attributes=[
                *ISSUE_ATTRIBUTES,
                EntityAttribute(
                    name="Work item lead time in days",
                    key="lead_time",
                    type=EntityAttributeType.INTEGER,
                ),
            ],
        ),
        "failed_jobs": Entity(name="failed pipeline", attributes=PIPELINE_ATTRIBUTES),
        "job_runs_within_time_period": Entity(name="pipeline", attributes=PIPELINE_ATTRIBUTES),
        "merge_requests": Entity(
            name="merge request",
            attributes=[
                EntityAttribute(name="Merge request", key="title", url="url"),
                EntityAttribute(name="Target branch", key="target_branch"),
                EntityAttribute(name="State"),
                EntityAttribute(name="Upvotes", type=EntityAttributeType.INTEGER),
                EntityAttribute(name="Downvotes", type=EntityAttributeType.INTEGER),
                EntityAttribute(name="Created", type=EntityAttributeType.DATETIME),
                EntityAttribute(name="Closed", type=EntityAttributeType.DATETIME),
            ],
        ),
        "tests": Entity(
            name="test run",
            measured_attribute="counted_tests",
            attributes=[
                EntityAttribute(name="Test run name", key="name", url="url"),
                EntityAttribute(name="Test run state", key="state"),
                EntityAttribute(name="Build id"),
                EntityAttribute(name="Started date", type=EntityAttributeType.DATETIME),
                EntityAttribute(name="Completed date", type=EntityAttributeType.DATETIME),
                EntityAttribute(name="Incomplete tests", type=EntityAttributeType.INTEGER),
                EntityAttribute(name="Not applicable tests", type=EntityAttributeType.INTEGER),
                EntityAttribute(name="Passed tests", type=EntityAttributeType.INTEGER),
                EntityAttribute(name="Failed tests", key="unanalyzed_tests", type=EntityAttributeType.INTEGER),
                EntityAttribute(name="Total tests", type=EntityAttributeType.INTEGER),
                EntityAttribute(name="Counted tests", type=EntityAttributeType.INTEGER, visible=False),
            ],
        ),
        "unused_jobs": Entity(name="unused pipeline", attributes=PIPELINE_ATTRIBUTES),
        "unmerged_branches": Entity(
            name="branch",
            name_plural="branches",
            attributes=[
                EntityAttribute(name="Branch name", key="name", url="url"),
                EntityAttribute(
                    name="Date of most recent commit",
                    key="commit_date",
                    type=EntityAttributeType.DATE,
                ),
            ],
        ),
        "issues": Entity(name="issue", attributes=ISSUE_ATTRIBUTES),
        "user_story_points": Entity(
            name="user story",
            name_plural="user stories",
            measured_attribute="story_points",
            attributes=[
                EntityAttribute(name="Project"),
                EntityAttribute(name="Title", url="url"),
                EntityAttribute(name="Work item type"),
                EntityAttribute(name="State"),
                EntityAttribute(name="Story points", type=EntityAttributeType.INTEGER),
            ],
        ),
    },
)
