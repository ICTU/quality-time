"""GitLab source."""

from pydantic import HttpUrl

from shared_data_model.meta.entity import Color, Entity, EntityAttribute, EntityAttributeType
from shared_data_model.meta.source import Source
from shared_data_model.parameters import (
    URL,
    Branch,
    Branches,
    BranchesToIgnore,
    BranchMergeStatus,
    Days,
    FailureType,
    MergeRequestState,
    MultipleChoiceWithAdditionParameter,
    MultipleChoiceWithDefaultsParameter,
    PrivateToken,
    ResultType,
    SingleChoiceParameter,
    StringParameter,
    TargetBranchesToInclude,
    Upvotes,
)

ALL_GITLAB_METRICS = [
    "change_failure_rate",
    "failed_jobs",
    "inactive_branches",
    "job_runs_within_time_period",
    "merge_requests",
    "pipeline_duration",
    "source_up_to_dateness",
    "source_version",
    "unused_jobs",
]

JOB_ENTITY_ATTRIBUTES = [
    EntityAttribute(name="Job name", key="name", url="url"),
    EntityAttribute(name="Job stage", key="stage"),
    EntityAttribute(name="Branch or tag", key="branch"),
]

JOB_ENTITY = Entity(
    name="job",
    attributes=[
        *JOB_ENTITY_ATTRIBUTES,
        EntityAttribute(
            name="Result of most recent build",
            key="build_result",
            color={
                "canceled": Color.ACTIVE,
                "failed": Color.NEGATIVE,
                "skipped": Color.WARNING,
                "success": Color.POSITIVE,
            },
        ),
        EntityAttribute(name="Date of most recent build", key="build_date", type=EntityAttributeType.DATE),
    ],
)

PIPELINE_ENTITY = Entity(
    name="pipeline",
    attributes=[
        EntityAttribute(name="Pipeline name", key="name", url="url"),
        EntityAttribute(name="Ref"),
        EntityAttribute(name="Status"),
        EntityAttribute(name="Trigger"),
        EntityAttribute(name="Schedule"),
        EntityAttribute(name="Created", type=EntityAttributeType.DATETIME),
        EntityAttribute(name="Updated", type=EntityAttributeType.DATETIME),
        EntityAttribute(name="Duration (minutes)", key="duration", type=EntityAttributeType.INTEGER),
    ],
)

GITLAB_BRANCH_HELP_URL = HttpUrl("https://docs.gitlab.com/ee/user/project/repository/branches/")

GITLAB = Source(
    name="GitLab",
    description="GitLab provides Git-repositories, wiki's, issue-tracking and continuous integration/continuous "
    "deployment pipelines.",
    url=HttpUrl("https://about.gitlab.com/"),
    documentation={
        "generic": """```{note}
Some metric sources are documents in JSON, XML, CSV, or HTML format. Examples include JUnit XML reports, JaCoCo XML
reports and Axe CSV reports. Usually, you add a JUnit (or JaCoCo, or Axe...) source and then simply configure the same
URL that you use to access the document via the browser. Unfortunately, this does not work if the document is stored in
GitLab. In that case, you still use the JUnit (or JaCoCo, or Axe...) source, but provide a GitLab API URL as URL.
Depending on where the document is stored in GitLab, there are two scenarios; the source is a build artifact of a GitLab
CI pipeline, or the source is stored in a GitLab repository:

1. When the metric source is a build artifact of a GitLab CI pipeline, use [URLs of the following format](https://docs.gitlab.com/api/job_artifacts/#download-a-single-artifact-file-by-reference-name):

    `https://<gitlab-server>/api/v4/projects/<project-id>/jobs/artifacts/<branch>/raw/<path>/<to>/<file-name>?\
job=<job-name>`

    The project id can be found under the
    [project's general settings](https://docs.gitlab.com/ee/user/project/settings/).

    If the repository is private, you also need to enter an [personal access token](https://docs.gitlab.com/ee/user/\
profile/personal_access_tokens.html) with the scope `read_api` in the private token field.

    ```{warning}
    Artifacts can only be downloaded from a
    [completed pipeline with status `success`](https://docs.gitlab.com/api/job_artifacts/#download-a-single-artifact-file-by-reference-name).
    Consider setting `allow_failure: true` on
    [test jobs](https://docs.gitlab.com/ci/quick_start/tutorial/#add-test-jobs) in the pipeline.
    ```

2.  When the metric source is a file stored in a GitLab repository, use [URLs of the following format](https://docs.\
gitlab.com/ee/api/repository_files.html#get-raw-file-from-repository):

    `https://<gitlab-server>/api/v4/projects/<project-id>/repository/files/<file-path-with-slashes-%2F-encoded>/raw?\
ref=<branch>`

    The project id can be found under the
    [project's general settings](https://docs.gitlab.com/ee/user/project/settings/).

    If the repository is private, you also need to enter an [personal access token](https://docs.gitlab.com/ee/user/\
profile/personal_access_tokens.html) with the scope `read_repository` in the private token field.
```""",
    },
    parameters={
        "url": URL(
            name="GitLab instance URL",
            help="URL of the GitLab instance, with port if necessary, but without path. For example, "
            "'https://gitlab.com'.",
            validate_on=["private_token"],
            metrics=ALL_GITLAB_METRICS,
        ),
        "project": StringParameter(
            name="Project (name with namespace or id)",
            mandatory=True,
            help_url=HttpUrl("https://docs.gitlab.com/ee/user/project/"),
            metrics=[
                "change_failure_rate",
                "failed_jobs",
                "job_runs_within_time_period",
                "pipeline_duration",
                "merge_requests",
                "source_up_to_dateness",
                "unused_jobs",
            ],
        ),
        "project_or_group": StringParameter(
            name="Project (name with namespace or id) or group (name or id)",
            mandatory=True,
            help_url=HttpUrl("https://docs.gitlab.com/ee/user/project/"),
            metrics=["inactive_branches"],
        ),
        "private_token": PrivateToken(
            name="Private token (with read_api scope)",
            help_url=HttpUrl("https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html"),
            metrics=ALL_GITLAB_METRICS,
        ),
        "file_path": StringParameter(
            name="File or folder path",
            help="Use the date and time the path was last changed to determine the up-to-dateness. If no path "
            "is specified, the pipeline is used to determine the up-to-dateness.",
            metrics=["source_up_to_dateness"],
        ),
        "branch": Branch(help_url=GITLAB_BRANCH_HELP_URL),
        "branches": Branches(help_url=GITLAB_BRANCH_HELP_URL),
        "branches_to_ignore": BranchesToIgnore(help_url=GITLAB_BRANCH_HELP_URL),
        "branch_merge_status": BranchMergeStatus(),
        "refs_to_ignore": MultipleChoiceWithAdditionParameter(
            name="Branches and tags to ignore (regular expressions, branch names or tag names)",
            help_url=GITLAB_BRANCH_HELP_URL,
            metrics=["change_failure_rate", "failed_jobs", "job_runs_within_time_period", "unused_jobs"],
        ),
        "refs_to_include": MultipleChoiceWithAdditionParameter(
            name="Branches and tags to include (regular expressions, branch names or tag names)",
            help_url=GITLAB_BRANCH_HELP_URL,
            placeholder="all branches and tags",
            metrics=["change_failure_rate", "failed_jobs", "job_runs_within_time_period", "unused_jobs"],
        ),
        "inactive_days": Days(
            name="Number of days since last commit after which to consider branches inactive",
            default_value="7",
            metrics=["inactive_branches"],
        ),
        "inactive_job_days": Days(
            name="Number of days without builds after which to consider CI-jobs unused",
            default_value="90",
            metrics=["unused_jobs"],
        ),
        "failure_type": FailureType(values=["canceled", "failed", "skipped"]),
        "result_type": ResultType(values=["canceled", "failed", "skipped", "success"]),
        "jobs_to_ignore": MultipleChoiceWithAdditionParameter(
            name="Jobs to ignore (regular expressions or job names)",
            help="Jobs to ignore can be specified by job name or by regular expression.",
            metrics=["change_failure_rate", "failed_jobs", "job_runs_within_time_period", "unused_jobs"],
        ),
        "jobs_to_include": MultipleChoiceWithAdditionParameter(
            name="Jobs to include (regular expressions or job names)",
            help="Jobs to include can be specified by job name or by regular expression.",
            placeholder="all jobs",
            metrics=["change_failure_rate", "failed_jobs", "job_runs_within_time_period", "unused_jobs"],
        ),
        "lookback_days": Days(
            name="Number of days to look back for selecting pipeline jobs",
            default_value="90",
            metrics=[
                "change_failure_rate",
                "failed_jobs",
                "job_runs_within_time_period",
                "source_up_to_dateness",
                "unused_jobs",
            ],
        ),
        "lookback_days_pipelines": Days(
            name="Number of days to look back for selecting pipelines",
            default_value="7",
            metrics=["pipeline_duration"],
        ),
        "merge_request_state": MergeRequestState(values=["opened", "locked", "merged", "closed"]),
        "approval_state": MultipleChoiceWithDefaultsParameter(
            name="Approval states to include (requires GitLab Premium)",
            help_url=HttpUrl("https://docs.gitlab.com/ee/user/project/merge_requests/approvals/"),
            values=["approved", "not approved", "unknown"],
            api_values={"approved": "yes", "not approved": "no", "unknown": "?"},
            placeholder="all approval states",
            metrics=["merge_requests"],
        ),
        "pipeline_statuses_to_include": MultipleChoiceWithDefaultsParameter(
            name="Pipeline statuses to include",
            values=[
                "created",
                "waiting for resource",
                "preparing",
                "pending",
                "running",
                "success",
                "failed",
                "canceled",
                "skipped",
                "manual",
                "scheduled",
            ],
            api_values={"waiting for resource": "waiting_for_resource"},
            placeholder="all pipeline statuses",
            metrics=["pipeline_duration", "source_up_to_dateness"],
        ),
        "pipeline_triggers_to_include": MultipleChoiceWithDefaultsParameter(
            name="Pipeline triggers to include",
            values=[
                "push",
                "web",
                "trigger",
                "schedule",
                "api",
                "external",
                "pipeline",
                "chat",
                "web-IDE",
                "merge request event",
                "external pull request event",
                "parent pipeline",
                "ondemand DAST scan",
                "ondemand DAST validation",
            ],
            api_values={
                "merge request event": "merge_request_event",
                "external pull request event": "external_pull_request_event",
                "parent pipeline": "parent_pipeline",
                "ondemand DAST scan": "ondemand_dast_scan",
                "ondemand DAST validation": "ondemand_dast_validation",
                "web-IDE": "webide",
            },
            placeholder="all pipeline triggers",
            metrics=["pipeline_duration", "source_up_to_dateness"],
        ),
        "pipeline_schedules_to_include": MultipleChoiceWithAdditionParameter(
            name="Pipeline schedules to include",
            help="Pipeline schedules to include can be specified by description or by regular expression.",
            placeholder="all pipeline schedules",
            metrics=["pipeline_duration", "source_up_to_dateness"],
        ),
        "pipeline_selection": SingleChoiceParameter(
            name="Pipeline selection",
            help="Which pipeline(s) to select from the set of pipelines that match the filter criteria?",
            values=["average", "latest", "slowest"],
            default_value="slowest",
            metrics=["pipeline_duration"],
        ),
        "upvotes": Upvotes(),
        "target_branches_to_include": TargetBranchesToInclude(help_url=GITLAB_BRANCH_HELP_URL),
    },
    entities={
        "change_failure_rate": Entity(
            name="deployment",
            attributes=[
                EntityAttribute(name="Job name", key="name", url="url"),
                EntityAttribute(name="Job stage", key="stage"),
                EntityAttribute(name="Branch or tag", key="branch"),
                EntityAttribute(name="Status of most recent build", key="build_status"),
                EntityAttribute(name="Date of most recent build", key="build_date", type=EntityAttributeType.DATE),
            ],
        ),
        "failed_jobs": Entity(
            name="job",
            attributes=[
                *JOB_ENTITY_ATTRIBUTES,
                EntityAttribute(
                    name="Result of most recent failed build",
                    key="build_result",
                    color={
                        "canceled": Color.ACTIVE,
                        "failed": Color.NEGATIVE,
                        "skipped": Color.WARNING,
                    },
                ),
                EntityAttribute(
                    name="Date of most recent failed build", key="build_date", type=EntityAttributeType.DATE
                ),
            ],
        ),
        "job_runs_within_time_period": JOB_ENTITY,
        "merge_requests": Entity(
            name="merge request",
            attributes=[
                EntityAttribute(name="Merge request", key="title", url="url"),
                EntityAttribute(name="Target branch"),
                EntityAttribute(name="State"),
                EntityAttribute(name="Approved"),
                EntityAttribute(name="Upvotes", type=EntityAttributeType.INTEGER),
                EntityAttribute(name="Downvotes", type=EntityAttributeType.INTEGER),
                EntityAttribute(name="Created", type=EntityAttributeType.DATETIME),
                EntityAttribute(name="Updated", type=EntityAttributeType.DATETIME),
                EntityAttribute(name="Merged", type=EntityAttributeType.DATETIME),
            ],
        ),
        "inactive_branches": Entity(
            name="branch",
            name_plural="branches",
            attributes=[
                EntityAttribute(name="Branch name", key="name", url="url"),
                EntityAttribute(
                    name="Date of most recent commit",
                    key="commit_date",
                    type=EntityAttributeType.DATE,
                ),
                EntityAttribute(name="Merge status"),
            ],
        ),
        "pipeline_duration": PIPELINE_ENTITY,
        "unused_jobs": JOB_ENTITY,
    },
)
