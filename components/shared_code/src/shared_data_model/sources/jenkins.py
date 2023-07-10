"""Jenkins source."""

from shared_data_model.meta.entity import Color, EntityAttributeType
from shared_data_model.meta.parameter import Parameter
from shared_data_model.meta.source import Source
from shared_data_model.parameters import (
    Days,
    FailureType,
    MultipleChoiceParameter,
    MultipleChoiceWithAdditionParameter,
    TestResult,
    access_parameters,
)

AUTHENTICATION_URL = "https://www.jenkins.io/doc/book/system-administration/authenticating-scripted-clients/"


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
    "failed_jobs",
    "job_runs_within_time_period",
    "source_up_to_dateness",
    "source_version",
    "unused_jobs",
]

JOB_ENTITY = {
    "name": "job",
    "attributes": [
        {"name": "Job name", "key": "name", "url": "url"},
        {
            "name": "Status of most recent build",
            "key": "build_status",
            "color": {
                "Success": Color.POSITIVE,
                "Failure": Color.NEGATIVE,
                "Aborted": Color.ACTIVE,
                "Unstable": Color.WARNING,
            },
        },
        {"name": "Date of most recent build", "key": "build_date", "type": EntityAttributeType.DATE},
    ],
}

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
    url="https://www.jenkins.io/",
    parameters=dict(
        inactive_days=Days(
            name="Number of days without builds after which to consider CI-jobs unused",
            short_name="number of days without builds",
            default_value="90",
            metrics=["unused_jobs"],
        ),
        jobs_to_include=MultipleChoiceWithAdditionParameter(
            name="Jobs to include (regular expressions or job names)",
            short_name="jobs to include",
            help="Jobs to include can be specified by job name or by regular expression. "
            "Use {parent job name}/{child job name} for the names of nested jobs.",
            placeholder="all",
            metrics=["failed_jobs", "job_runs_within_time_period", "source_up_to_dateness", "unused_jobs"],
        ),
        jobs_to_ignore=MultipleChoiceWithAdditionParameter(
            name="Jobs to ignore (regular expressions or job names)",
            short_name="jobs to ignore",
            help="Jobs to ignore can be specified by job name or by regular expression. "
            "Use {parent job name}/{child job name} for the names of nested jobs.",
            metrics=["failed_jobs", "job_runs_within_time_period", "source_up_to_dateness", "unused_jobs"],
        ),
        lookback_days=Days(
            name="Number of days to look back for selecting job builds",
            short_name="number of days to look back",
            default_value="90",
            metrics=["job_runs_within_time_period"],
        ),
        result_type=MultipleChoiceParameter(
            name="Build result types",
            short_name="result types",
            help="Limit which build result types to include.",
            placeholder="all result types",
            values=["Aborted", "Failure", "Not built", "Success", "Unstable"],
            metrics=["source_up_to_dateness"],
        ),
        failure_type=FailureType(values=["Aborted", "Failure", "Not built", "Unstable"]),
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
    ),
    entities={
        "failed_jobs": JOB_ENTITY,
        "job_runs_within_time_period": {
            "name": "build",
            "attributes": [
                {"name": "Job name", "key": "name", "url": "url"},
                {"name": "Number of builds in time period", "key": "build_count", "type": EntityAttributeType.INTEGER},
            ],
        },
        "source_up_to_dateness": JOB_ENTITY,
        "unused_jobs": JOB_ENTITY,
    },
)

ALL_JENKINS_TEST_REPORT_METRICS = ["source_up_to_dateness", "test_cases", "tests"]

TEST_ENTITIES = {
    "name": "test",
    "attributes": [
        {"name": "Class name"},
        {"name": "Test case", "key": "name"},
        {
            "name": "Test result",
            "color": {"failed": Color.NEGATIVE, "passed": Color.POSITIVE, "skipped": Color.WARNING},
        },
        {"name": "Number of builds the test has been failing", "key": "age", "type": EntityAttributeType.INTEGER},
    ],
}

JENKINS_TEST_REPORT = Source(
    name="Jenkins test report",
    description="A Jenkins job with test results.",
    documentation={
        "test_cases": JENKINS_TOKEN_DOCS,
        "tests": JENKINS_TOKEN_DOCS,
        "source_up_to_dateness": JENKINS_TOKEN_DOCS,
    },
    url="https://plugins.jenkins.io/junit",
    parameters=dict(
        test_result=TestResult(values=["failed", "passed", "skipped"]),
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
    ),
    entities={"tests": TEST_ENTITIES, "test_cases": TEST_ENTITIES},
)
