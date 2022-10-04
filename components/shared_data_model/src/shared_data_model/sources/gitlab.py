"""GitLab source."""

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
    URL,
)


ALL_GITLAB_METRICS = [
    "failed_jobs",
    "job_runs_within_time_period",
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
    url="https://about.gitlab.com/",
    documentation=dict(
        generic="""```{note}
Some metric sources are documents in JSON, XML, CSV, or HTML format. Examples include JUnit XML reports, JaCoCo XML
reports and Axe CSV reports. Usually, you add a JUnit (or JaCoCo, or Axe...) source and then simply configure the same
URL that you use to access the document via the browser. Unfortunately, this does not work if the document is stored in
GitLab. In that case, you still use the JUnit (or JaCoCo, or Axe...) source, but provide a GitLab API URL as URL.
Depending on where the document is stored in GitLab, there are two scenarios; the source is a build artifact of a GitLab
CI pipeline, or the source is stored in a GitLab repository:

1. When the metric source is a build artifact of a GitLab CI pipeline, use [URLs of the following format](https://docs.\
gitlab.com/ee/api/job_artifacts.html#download-a-single-artifact-file-from-specific-tag-or-branch):

    `https://<gitlab-server>/api/v4/projects/<project-id>/jobs/artifacts/<branch>/raw/<path>/<to>/<file-name>?\
job=<job-name>`

    The project id can be found under the
    [project's general settings](https://docs.gitlab.com/ee/user/project/settings/).

    If the repository is private, you also need to enter an [personal access token](https://docs.gitlab.com/ee/user/\
profile/personal_access_tokens.html) with the scope `read_api` in the private token field.

2.  When the metric source is a file stored in a GitLab repository, use [URLs of the following format](https://docs.\
gitlab.com/ee/api/repository_files.html#get-raw-file-from-repository):

    `https://<gitlab-server>/api/v4/projects/<project-id>/repository/files/<file-path-with-slashes-%2F-encoded>/raw?\
ref=<branch>`

    The project id can be found under the
    [project's general settings](https://docs.gitlab.com/ee/user/project/settings/).

    If the repository is private, you also need to enter an [personal access token](https://docs.gitlab.com/ee/user/\
profile/personal_access_tokens.html) with the scope `read_repository` in the private token field.
```"""
    ),
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
                "job_runs_within_time_period",
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
            metrics=["failed_jobs", "job_runs_within_time_period", "unused_jobs"],
        ),
        inactive_days=Days(
            name="Number of days since last commit after which to consider branches inactive",
            short_name="number of days since last commit",
            default_value="7",
            metrics=["unmerged_branches"],
        ),
        inactive_job_days=Days(
            name="Number of days without builds after which to consider CI-jobs unused",
            short_name="number of days without builds",
            default_value="90",
            metrics=["unused_jobs"],
        ),
        failure_type=FailureType(values=["canceled", "failed", "skipped"]),
        jobs_to_ignore=MultipleChoiceWithAdditionParameter(
            name="Jobs to ignore (regular expressions or job names)",
            short_name="jobs to ignore",
            help="Jobs to ignore can be specified by job name or by regular expression.",
            metrics=["failed_jobs", "job_runs_within_time_period", "unused_jobs"],
        ),
        lookback_days=Days(
            name="Number of days to look back in selecting job builds to consider",
            short_name="number of days to look back",
            default_value="90",
            metrics=["job_runs_within_time_period"],
        ),
        merge_request_state=MergeRequestState(values=["opened", "locked", "merged", "closed"]),
        approval_state=MultipleChoiceParameter(
            name="Approval states to include (requires GitLab Premium)",
            short_name="approval states",
            help_url="https://docs.gitlab.com/ee/user/project/merge_requests/approvals/",
            values=["approved", "not approved", "unknown"],
            api_values={"approved": "yes", "not approved": "no", "unknown": "?"},
            placeholder="all approval states",
            metrics=["merge_requests"],
        ),
        upvotes=Upvotes(),
        target_branches_to_include=TargetBranchesToInclude(help_url=GITLAB_BRANCH_HELP_URL),
    ),
    entities=dict(
        failed_jobs=JOB_ENTITY,
        job_runs_within_time_period=JOB_ENTITY,
        merge_requests=dict(
            name="merge request",
            attributes=[
                dict(name="Merge request", key="title", url="url"),
                dict(name="Target branch"),
                dict(name="State"),
                dict(name="Approved"),
                dict(name="Upvotes", type=EntityAttributeType.INTEGER),
                dict(name="Downvotes", type=EntityAttributeType.INTEGER),
                dict(name="Created", type=EntityAttributeType.DATETIME),
                dict(name="Updated", type=EntityAttributeType.DATETIME),
                dict(name="Merged", type=EntityAttributeType.DATETIME),
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
