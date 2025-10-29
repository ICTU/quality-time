"""Jenkins source."""

from typing import TYPE_CHECKING

from pydantic import HttpUrl

from shared_data_model.meta.entity import Color, Entity, EntityAttribute, EntityAttributeType
from shared_data_model.meta.source import Source
from shared_data_model.parameters import (
    Branches,
    Days,
    FailureType,
    MultipleChoiceWithAdditionParameter,
    ResultType,
    SingleChoiceParameter,
    StringParameter,
    TestResult,
    TestResultAggregationStrategy,
    access_parameters,
)

if TYPE_CHECKING:
    from shared_data_model.meta.parameter import Parameter


AUTHENTICATION_URL = HttpUrl("https://www.jenkins.io/doc/book/system-administration/authenticating-scripted-clients/")


def jenkins_access_parameters(*args, **kwargs) -> dict[str, Parameter]:
    """Create Jenkins specific access parameters."""
    kwargs["include"] = {"private_token": False, "landing_url": False}
    if "name" not in kwargs.setdefault("kwargs", {}).setdefault("url", {}):
        kwargs["kwargs"]["url"]["name"] = "URL to Jenkins job"
    kwargs["kwargs"]["password"] = {
        "name": "Password or API token for basic authentication",
        "help_url": AUTHENTICATION_URL,
    }
    return access_parameters(*args, **kwargs)


# Put the Jenkins token documentation in a temporary variable that doesn't trigger a security warning so we can
# suppress the false positive Bandit warning below.
_TMP_DOC = f"""To authorize *Quality-time* for (non-public resources in) Jenkins, you can either use a username and
password or a username and [API token]({AUTHENTICATION_URL}). Note that, unlike other sources, when using the API token
Jenkins also requires the username to which the token belongs."""
JENKINS_TOKEN_DOCS = _TMP_DOC  # nosec hardcoded_password_string

ALL_JENKINS_METRICS = [
    "change_failure_rate",
    "failed_jobs",
    "job_runs_within_time_period",
    "pipeline_duration",
    "source_up_to_dateness",
    "source_version",
    "unused_jobs",
]

_JOB_ENTITY_NAME_NAME = "Job name"
JOB_ENTITY = Entity(
    name="job",
    attributes=[
        EntityAttribute(name=_JOB_ENTITY_NAME_NAME, key="name", url="url"),
        EntityAttribute(
            name="Result of most recent build",
            key="build_result",
            color={
                "Success": Color.POSITIVE,
                "Failure": Color.NEGATIVE,
                "Aborted": Color.ACTIVE,
                "Unstable": Color.WARNING,
            },
        ),
        EntityAttribute(name="Date of most recent build", key="build_date", type=EntityAttributeType.DATE),
    ],
)

JENKINS = Source(
    name="Jenkins",
    description="Jenkins is an open source continuous integration/continuous deployment server.",
    documentation={
        "generic": f"""```{{note}}
Some metric sources are documents in JSON, XML, CSV, or HTML format. Examples include JUnit XML reports, JaCoCo XML
reports and Axe CSV reports. Usually, you add a JUnit (or JaCoCo, or Axe...) source and then simply configure the same
URL that you use to access the document via the browser. If the document is stored in Jenkins and *Quality-time* needs
to be authorized to access resources in Jenkins, there are [two options]({AUTHENTICATION_URL}):

1. Configure a Jenkins user and password. The username of the Jenkins user needs to be entered in the "Username" field
and the password in the "Password" field.

2. Configure a Jenkins user and a private token of that user. The username of the Jenkins user needs to be entered in
the "Username" field and the private token in the "**Password**" field.
```""",
        "unused_jobs": JENKINS_TOKEN_DOCS,
        "failed_jobs": JENKINS_TOKEN_DOCS,
        "source_up_to_dateness": JENKINS_TOKEN_DOCS,
        "source_version": JENKINS_TOKEN_DOCS,
    },
    url=HttpUrl("https://www.jenkins.io/"),
    parameters={
        "branches": Branches(help="Branches only apply to multibranch pipelines."),
        "inactive_days": Days(
            name="Number of days without builds after which to consider CI-jobs unused",
            default_value="90",
            metrics=["unused_jobs"],
        ),
        "jobs_to_include": MultipleChoiceWithAdditionParameter(
            name="Jobs to include (regular expressions or job names)",
            help="Jobs to include can be specified by job name or by regular expression. "
            "Use {parent job name}/{child job name} for the names of nested jobs.",
            placeholder="all",
            metrics=[
                "change_failure_rate",
                "failed_jobs",
                "job_runs_within_time_period",
                "source_up_to_dateness",
                "unused_jobs",
            ],
        ),
        "jobs_to_ignore": MultipleChoiceWithAdditionParameter(
            name="Jobs to ignore (regular expressions or job names)",
            help="Jobs to ignore can be specified by job name or by regular expression. "
            "Use {parent job name}/{child job name} for the names of nested jobs.",
            metrics=[
                "change_failure_rate",
                "failed_jobs",
                "job_runs_within_time_period",
                "source_up_to_dateness",
                "unused_jobs",
            ],
        ),
        "grace_days": Days(
            name="Number of days after which to count failed jobs as failed",
            help="Count failed jobs as failed only when it has been failing for at least the number of 'grace days'.",
            min_value="0",
            default_value="0",
            metrics=["failed_jobs"],
        ),
        "lookback_days": Days(
            name="Number of days to look back for selecting job builds",
            default_value="90",
            metrics=["change_failure_rate", "job_runs_within_time_period"],
        ),
        "pipeline": StringParameter(
            name="Pipeline (multibranch pipeline name)",
            mandatory=True,
            metrics=["pipeline_duration"],
        ),
        "pipeline_selection": SingleChoiceParameter(
            name="Pipeline selection",
            help="Which pipeline(s) to select from the set of pipelines that match the filter criteria?",
            values=["average", "latest", "slowest"],
            default_value="slowest",
            metrics=["pipeline_duration"],
        ),
        "result_type": ResultType(
            values=["Aborted", "Failure", "Not built", "Success", "Unstable"],
            metrics=["job_runs_within_time_period", "pipeline_duration", "source_up_to_dateness"],
        ),
        "failure_type": FailureType(values=["Aborted", "Failure", "Not built", "Unstable"]),
        **jenkins_access_parameters(
            ALL_JENKINS_METRICS,
            kwargs={
                "url": {
                    "name": "URL",
                    "help": "URL of the Jenkins instance, with port if necessary, but without path. For example, "
                    "'https://jenkins.example.org'.",
                },
            },
        ),
    },
    entities={
        "change_failure_rate": Entity(
            name="deployment",
            attributes=[
                EntityAttribute(name=_JOB_ENTITY_NAME_NAME, key="name", url="url"),
                EntityAttribute(name="Result of most recent build", key="build_result"),
                EntityAttribute(name="Date of most recent build", key="build_date", type=EntityAttributeType.DATE),
            ],
        ),
        "failed_jobs": JOB_ENTITY,
        "job_runs_within_time_period": Entity(
            name="build",
            attributes=[
                EntityAttribute(name=_JOB_ENTITY_NAME_NAME, key="name", url="url"),
                EntityAttribute(
                    name="Number of builds in time period",
                    key="build_count",
                    type=EntityAttributeType.INTEGER,
                ),
            ],
        ),
        "source_up_to_dateness": JOB_ENTITY,
        "unused_jobs": JOB_ENTITY,
    },
)

ALL_JENKINS_TEST_REPORT_METRICS = ["source_up_to_dateness", "test_cases", "tests"]

TEST_ENTITIES = Entity(
    name="test",
    attributes=[
        EntityAttribute(name="Class name"),
        EntityAttribute(name="Test case", key="name"),
        EntityAttribute(
            name="Test result",
            color={"failed": Color.NEGATIVE, "passed": Color.POSITIVE, "skipped": Color.WARNING},
        ),
        EntityAttribute(name="Number of builds the test has been failing", key="age", type=EntityAttributeType.INTEGER),
    ],
)

JENKINS_TEST_REPORT = Source(
    name="Jenkins test report",
    description="A Jenkins job with test results.",
    documentation={
        "test_cases": JENKINS_TOKEN_DOCS,
        "tests": JENKINS_TOKEN_DOCS,
        "source_up_to_dateness": JENKINS_TOKEN_DOCS,
    },
    url=HttpUrl("https://plugins.jenkins.io/junit"),
    parameters={
        "test_result": TestResult(values=["failed", "passed", "skipped"]),
        "test_result_aggregation_strategy": TestResultAggregationStrategy(),
        **jenkins_access_parameters(
            ALL_JENKINS_TEST_REPORT_METRICS,
            kwargs={
                "url": {
                    "help": "URL to a Jenkins job with a test report generated by the JUnit plugin. For example, "
                    "'https://jenkins.example.org/job/test' or https://jenkins.example.org/job/test/job/main' "
                    "in case of a pipeline job.",
                },
            },
        ),
    },
    entities={"tests": TEST_ENTITIES, "test_cases": TEST_ENTITIES},
)
