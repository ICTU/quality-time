"""JaCoCo source."""

from pydantic import HttpUrl

from shared_data_model.meta.source import Source
from shared_data_model.parameters import access_parameters

from .jenkins import JENKINS_TOKEN_DOCS, jenkins_access_parameters

ALL_JACOCO_METRICS = ["source_up_to_dateness", "uncovered_branches", "uncovered_lines"]

JACOCO = Source(
    name="JaCoCo",
    description="JaCoCo is an open-source tool for measuring and reporting Java code coverage.",
    url=HttpUrl("https://www.eclemma.org/jacoco/"),
    parameters=access_parameters(ALL_JACOCO_METRICS, source_type="JaCoCo report", source_type_format="XML"),
)

JACOCO_JENKINS_PLUGIN = Source(
    name="JaCoCo Jenkins plugin",
    description="A Jenkins job with a JaCoCo coverage report produced by the JaCoCo Jenkins plugin.",
    documentation={
        "source_up_to_dateness": JENKINS_TOKEN_DOCS,
        "uncovered_branches": JENKINS_TOKEN_DOCS,
        "uncovered_lines": JENKINS_TOKEN_DOCS,
    },
    url=HttpUrl("https://plugins.jenkins.io/jacoco"),
    parameters=jenkins_access_parameters(
        ALL_JACOCO_METRICS,
        kwargs={
            "url": {
                "help": "URL to a Jenkins job with a coverage report generated by the JaCoCo plugin. For example, "
                "'https://jenkins.example.org/job/jacoco' or https://jenkins.example.org/job/jacoco/job/main' in "
                "case of a pipeline job.",
            },
        },
    ),
)
