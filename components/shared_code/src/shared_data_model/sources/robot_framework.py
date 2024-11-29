"""Robot Framework source."""

from pydantic import HttpUrl

from shared_data_model.meta.entity import Color, Entity, EntityAttribute
from shared_data_model.meta.source import Source
from shared_data_model.parameters import TestResult, access_parameters

from .jenkins import JENKINS_TOKEN_DOCS, jenkins_access_parameters

ALL_ROBOT_FRAMEWORK_METRICS = ["source_up_to_dateness", "source_version", "test_cases", "tests"]

ROBOT_FRAMEWORK = Source(
    name="Robot Framework",
    description="Robot Framework is a generic open source automation framework for acceptance testing, acceptance "
    "test driven development, and robotic process automation.",
    url=HttpUrl("https://robotframework.org"),
    parameters={
        "test_result": TestResult(values=["fail", "pass", "skip"]),
        **access_parameters(
            ALL_ROBOT_FRAMEWORK_METRICS,
            source_type="Robot Framework report",
            source_type_format="XML",
        ),
    },
    entities={
        "tests": Entity(
            name="test",
            attributes=[
                EntityAttribute(name="Suite name"),
                EntityAttribute(name="Test name"),
                EntityAttribute(name="Test result", color={"fail": Color.NEGATIVE, "pass": Color.POSITIVE}),
            ],
        ),
    },
)

ALL_ROBOT_FRAMEWORK_JENKINS_PLUGIN_METRICS = ["source_up_to_dateness", "tests"]

ROBOT_FRAMEWORK_JENKINS_PLUGIN = Source(
    name="Robot Framework Jenkins plugin",
    description="A Jenkins plugin for Robot Framework, a generic open source automation framework for acceptance "
    "testing, acceptance test driven development, and robotic process automation.",
    documentation={"source_up_to_dateness": JENKINS_TOKEN_DOCS, "tests": JENKINS_TOKEN_DOCS},
    url=HttpUrl("https://plugins.jenkins.io/robot/"),
    parameters={
        "test_result": TestResult(
            values=["fail", "pass"],
            api_values={"fail": "overallFailed", "pass": "overallPassed"},
        ),
        **jenkins_access_parameters(
            ALL_ROBOT_FRAMEWORK_JENKINS_PLUGIN_METRICS,
            kwargs={
                "url": {
                    "help": "URL to a Jenkins job with a test report generated by the Robot Framework plugin. "
                    "For example, 'https://jenkins.example.org/job/robot' or "
                    "https://jenkins.example.org/job/robot/job/main' in case of a pipeline job.",
                },
            },
        ),
    },
)
