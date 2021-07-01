"""GitLab source."""

from ..meta.entity import Color, EntityAttributeType
from ..meta.source import Source
from ..parameters import (
    Branch,
    BranchesToIgnore,
    Days,
    FailureType,
    MergeRequestState,
    MultipleChoiceWithAdditionParameter,
    Upvotes,
    PrivateToken,
    StringParameter,
    TargetBranchesToInclude,
    URL,
)


ALL_GITLAB_METRICS = [
    "failed_jobs",
    "merge_requests",
    "source_up_to_dateness",
    "source_version",
    "unmerged_branches",
    "unused_jobs",
]

JOB_ENTITY = dict(
    name="job",
    attributes=[
        dict(name="Job name", key="name", url="url"),
        dict(name="Job stage", key="stage"),
        dict(name="Branch or tag", key="branch"),
        dict(
            name="Status of most recent build",
            key="build_status",
            color=dict(canceled=Color.ACTIVE, failed=Color.NEGATIVE, success=Color.POSITIVE),
        ),
        dict(name="Date of most recent build", key="build_date", type=EntityAttributeType.DATE),
    ],
)

GITLAB_BRANCH_HELP_URL = "https://docs.gitlab.com/ee/user/project/repository/branches/"

GITLAB = Source(
    name="GitLab",
    description="GitLab provides Git-repositories, wiki's, issue-tracking and continuous integration/continuous "
    "deployment pipelines.",
    url="https://gitlab.com/",
    parameters=dict(
        url=URL(
            name="GitLab instance URL",
            help="URL of the GitLab instance, with port if necessary, but without path. For example, "
            "'https://gitlab.com'.",
            validate_on=["private_token"],
            metrics=ALL_GITLAB_METRICS,
        ),
        project=StringParameter(
            name="Project (name with namespace or id)",
            short_name="project",
            mandatory=True,
            help_url="https://docs.gitlab.com/ee/user/project/",
            metrics=[
                "failed_jobs",
                "merge_requests",
                "source_up_to_dateness",
                "unmerged_branches",
                "unused_jobs",
            ],
        ),
        private_token=PrivateToken(
            name="Private token (with read_api scope)",
            help_url="https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html",
            metrics=ALL_GITLAB_METRICS,
        ),
        file_path=StringParameter(
            name="File or folder path",
            short_name="path",
            mandatory=True,
            help_url="https://docs.gitlab.com/ee/api/repository_files.html",
            metrics=["source_up_to_dateness"],
        ),
        branch=Branch(help_url=GITLAB_BRANCH_HELP_URL),
        branches_to_ignore=BranchesToIgnore(help_url=GITLAB_BRANCH_HELP_URL),
        refs_to_ignore=MultipleChoiceWithAdditionParameter(
            name="Branches and tags to ignore (regular expressions, branch names or tag names)",
            short_name="branches and tags to ignore",
            help_url=GITLAB_BRANCH_HELP_URL,
            metrics=["failed_jobs", "unused_jobs"],
        ),
        inactive_days=Days(
            name="Number of days since last commit after which to consider branches inactive",
            short_name="number of days since last commit",
            default_value="7",
            metrics=["unmerged_branches"],
        ),
        inactive_job_days=Days(
            name="Number of days without builds after which to consider CI-jobs unused.",
            short_name="number of days without builds",
            default_value="90",
            metrics=["unused_jobs"],
        ),
        failure_type=FailureType(values=["canceled", "failed", "skipped"]),
        jobs_to_ignore=MultipleChoiceWithAdditionParameter(
            name="Jobs to ignore (regular expressions or job names)",
            short_name="jobs to ignore",
            help="Jobs to ignore can be specified by job name or by regular expression.",
            metrics=["failed_jobs", "unused_jobs"],
        ),
        merge_request_state=MergeRequestState(values=["opened", "locked", "merged", "closed"]),
        upvotes=Upvotes(),
        target_branches_to_include=TargetBranchesToInclude(help_url=GITLAB_BRANCH_HELP_URL),
    ),
    entities=dict(
        failed_jobs=JOB_ENTITY,
        merge_requests=dict(
            name="merge request",
            attributes=[
                dict(name="Merge request", key="title", url="url"),
                dict(name="Target branch"),
                dict(name="State"),
                dict(name="Upvotes", type=EntityAttributeType.INTEGER),
                dict(name="Downvotes", type=EntityAttributeType.INTEGER),
                dict(name="Created", type=EntityAttributeType.DATETIME),
                dict(name="Updated", type=EntityAttributeType.DATETIME),
                dict(name="Merged", type=EntityAttributeType.DATETIME),
                dict(name="Closed", type=EntityAttributeType.DATETIME),
            ],
        ),
        unmerged_branches=dict(
            name="branch",
            name_plural="branches",
            attributes=[
                dict(name="Branch name", key="name", url="url"),
                dict(name="Date of most recent commit", key="commit_date", type=EntityAttributeType.DATE),
            ],
        ),
        unused_jobs=JOB_ENTITY,
    ),
)
