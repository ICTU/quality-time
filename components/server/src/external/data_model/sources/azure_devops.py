"""Azure DevOps source."""

from ..meta.entity import Color, EntityAttributeType
from ..meta.source import Source
from ..parameters import (
    Branch,
    BranchesToIgnore,
    Days,
    FailureType,
    MergeRequestState,
    MultipleChoiceParameter,
    MultipleChoiceWithAdditionParameter,
    Upvotes,
    PrivateToken,
    StringParameter,
    TargetBranchesToInclude,
    TestResult,
    URL,
)


ALL_AZURE_DEVOPS_METRICS = [
    "failed_jobs",
    "issues",
    "merge_requests",
    "user_story_points",
    "tests",
    "time_passed",
    "unmerged_branches",
    "unused_jobs",
]

PIPELINE_ATTRIBUTES = [
    dict(name="Pipeline", key="name", url="url"),
    dict(
        name="Status of most recent build",
        key="build_status",
        color=dict(
            succeeded=Color.POSITIVE, failed=Color.NEGATIVE, canceled=Color.ACTIVE, partiallySucceeded=Color.WARNING
        ),
    ),
    dict(name="Date of most recent build", key="build_date", type=EntityAttributeType.DATE),
]

AZURE_DEVOPS = Source(
    name="Azure DevOps Server",
    description="Azure DevOps Server (formerly known as Team Foundation Server) by Microsoft provides source code "
    "management, reporting, requirements management, project management, automated builds, testing and "
    "release management.",
    url="https://azure.microsoft.com/en-us/services/devops/server/",
    parameters=dict(
        url=URL(
            name="URL including organization and project",
            help="URL of the Azure DevOps instance, with port if necessary, and with organization and project. "
            "For example: 'https://dev.azure.com/{organization}/{project}'.",
            validate_on=["private_token"],
            metrics=ALL_AZURE_DEVOPS_METRICS,
        ),
        private_token=PrivateToken(
            help_url="https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/"
            "use-personal-access-tokens-to-authenticate?view=azure-devops",
            metrics=ALL_AZURE_DEVOPS_METRICS,
        ),
        wiql=StringParameter(
            name="Issue query in WIQL (Work Item Query Language)",
            short_name="issue query",
            mandatory=True,
            help_url="https://docs.microsoft.com/en-us/azure/devops/boards/queries/wiql-syntax?view=azure-devops",
            metrics=["issues", "user_story_points"],
        ),
        file_path=StringParameter(
            name="File or folder path",
            short_name="path",
            help="Use the date and time the path was last changed to determine the time passed. Note that if a "
            "pipeline is specified, the pipeline is used to determine the time passed, and the path is ignored.",
            placeholder="none",
            metrics=["time_passed"],
        ),
        repository=StringParameter(
            name="Repository (name or id)",
            short_name="repository",
            placeholder="default repository",
            metrics=["merge_requests", "unmerged_branches", "time_passed"],
        ),
        branch=Branch(),
        branches_to_ignore=BranchesToIgnore(
            help_url="https://docs.microsoft.com/en-us/azure/devops/repos/git/manage-your-branches?view=azure-devops",
        ),
        inactive_days=Days(
            name="Number of days since last commit after which to consider branches inactive",
            short_name="number of days since last commit",
            default_value="7",
            metrics=["unmerged_branches"],
        ),
        inactive_job_days=Days(
            name="Number of days since last build after which to consider pipelines inactive",
            short_name="number of days since last build",
            default_value="21",
            metrics=["unused_jobs"],
        ),
        test_result=TestResult(
            values=["incomplete", "failed", "not applicable", "passed"],
            api_values={
                "incomplete": "incompleteTests",
                "failed": "unanalyzedTests",
                "passed": "passedTests",
                "not applicable": "notApplicableTests",
            },
        ),
        test_run_names_to_include=MultipleChoiceWithAdditionParameter(
            name="Names of test runs to include (regular expressions or test run names)",
            short_name="test run names",
            help="Limit which test runs to include by test run name.",
            placeholder="all test run names",
            metrics=["tests"],
        ),
        test_run_states_to_include=MultipleChoiceParameter(
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
        jobs_to_include=MultipleChoiceWithAdditionParameter(
            name="Pipelines to include (regular expressions or pipeline names)",
            short_name="pipelines to include",
            help="Pipelines to include can be specified by pipeline name or by regular expression. "
            "Use {folder name}/{pipeline name} for the names of pipelines in folders.",
            placeholder="all",
            metrics=["failed_jobs", "unused_jobs", "time_passed"],
        ),
        jobs_to_ignore=MultipleChoiceWithAdditionParameter(
            name="Pipelines to ignore (regular expressions or pipeline names)",
            short_name="pipelines to ignore",
            help="Pipelines to ignore can be specified by pipeline name or by regular expression. "
            "Use {folder name}/{pipeline name} for the names of pipelines in folders.",
            metrics=["failed_jobs", "unused_jobs", "time_passed"],
        ),
        failure_type=FailureType(
            values=["canceled", "failed", "no result", "partially succeeded"],
            api_values={"no result": "none", "partially succeeded": "partiallySucceeded"},
        ),
        merge_request_state=MergeRequestState(
            values=["abandoned", "active", "completed", "not set"],
            api_values={"not set": "notSet"},
        ),
        upvotes=Upvotes(),
        target_branches_to_include=TargetBranchesToInclude(
            help_url="https://docs.microsoft.com/en-us/azure/devops/repos/git/manage-your-branches?view=azure-devops",
        ),
    ),
    entities=dict(
        failed_jobs=dict(
            name="failed pipeline",
            attributes=PIPELINE_ATTRIBUTES,
        ),
        merge_requests=dict(
            name="merge request",
            attributes=[
                dict(name="Merge request", key="title", url="url"),
                dict(name="Target branch", key="target_branch"),
                dict(name="State"),
                dict(name="Upvotes", type=EntityAttributeType.INTEGER),
                dict(name="Downvotes", type=EntityAttributeType.INTEGER),
                dict(name="Created", type=EntityAttributeType.DATETIME),
                dict(name="Closed", type=EntityAttributeType.DATETIME),
            ],
        ),
        tests=dict(
            name="test run",
            measured_attribute="counted_tests",
            attributes=[
                dict(name="Test run name", key="name", url="url"),
                dict(name="Test run state", key="state"),
                dict(name="Build id"),
                dict(name="Started date", type=EntityAttributeType.DATETIME),
                dict(name="Completed date", type=EntityAttributeType.DATETIME),
                dict(name="Incomplete tests", type=EntityAttributeType.INTEGER),
                dict(name="Not applicable tests", type=EntityAttributeType.INTEGER),
                dict(name="Passed tests", type=EntityAttributeType.INTEGER),
                dict(name="Failed tests", key="unanalyzed_tests", type=EntityAttributeType.INTEGER),
                dict(name="Total tests", type=EntityAttributeType.INTEGER),
                dict(name="Counted tests", type=EntityAttributeType.INTEGER, visible=False),
            ],
        ),
        unused_jobs=dict(name="unused pipeline", attributes=PIPELINE_ATTRIBUTES),
        unmerged_branches=dict(
            name="branch",
            name_plural="branches",
            attributes=[
                dict(name="Branch name", key="name", url="url"),
                dict(name="Date of most recent commit", key="commit_date", type=EntityAttributeType.DATE),
            ],
        ),
        issues=dict(
            name="issue",
            attributes=[
                dict(name="Project"),
                dict(name="Title", url="url"),
                dict(name="Work item type"),
                dict(name="State"),
            ],
        ),
        user_story_points=dict(
            name="user story",
            name_plural="user stories",
            measured_attribute="story_points",
            attributes=[
                dict(name="Project"),
                dict(name="Title", url="url"),
                dict(name="Work item type"),
                dict(name="State"),
                dict(name="Story points", type=EntityAttributeType.INTEGER),
            ],
        ),
    ),
)
