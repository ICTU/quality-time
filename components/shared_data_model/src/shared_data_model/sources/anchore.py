"""Anchore sources."""

from typing import cast

from shared_data_model.meta.entity import Color
from shared_data_model.meta.source import Source
from shared_data_model.parameters import URL, Severities, access_parameters

from .jenkins import JENKINS_TOKEN_DOCS, jenkins_access_parameters

ALL_ANCHORE_METRICS = ["security_warnings", "source_up_to_dateness"]

SEVERITIES = Severities(values=["Unknown", "Negligible", "Low", "Medium", "High", "Critical"])

COMMON_ENTITY_ATTRIBUTES = [
    {"name": "CVE", "url": "url"},
    {"name": "Package"},
    {"name": "Fix"},
    {
        "name": "Severity",
        "color": {"Critical": Color.NEGATIVE, "High": Color.NEGATIVE, "Medium": Color.WARNING, "Low": Color.WARNING},
    },
]

ANCHORE = Source(
    name="Anchore",
    description="Anchore image scan analysis report in JSON format.",
    url="https://docs.anchore.com/current/docs/using/integration/ci_cd/inline_scanning/",
    parameters=dict(
        details_url=URL(
            name="URL to an Anchore details report in JSON format or "
            "to a zip with Anchore details reports in JSON format",
            metrics=["source_up_to_dateness"],
        ),
        severities=SEVERITIES,
        **access_parameters(
            ALL_ANCHORE_METRICS,
            source_type="an Anchore vulnerability report",
            source_type_format="JSON",
            kwargs={"url": {"metrics": ["security_warnings"]}},
        ),
    ),
    entities={
        "security_warnings": {
            "name": "security warning",
            "attributes": [cast(object, {"name": "Report filename", "key": "filename"}), *COMMON_ENTITY_ATTRIBUTES],
        },
    },
)

ANCHORE_JENKINS_PLUGIN = Source(
    name="Anchore Jenkins plugin",
    description="A Jenkins job with an Anchore report produced by the Anchore Jenkins plugin.",
    documentation={"security_warnings": JENKINS_TOKEN_DOCS, "source_up_to_dateness": JENKINS_TOKEN_DOCS},
    url="https://plugins.jenkins.io/anchore-container-scanner/",
    parameters=dict(
        severities=SEVERITIES,
        **jenkins_access_parameters(
            ALL_ANCHORE_METRICS,
            kwargs={
                "url": {
                    "help": "URL to a Jenkins job with an Anchore report generated by the Anchore plugin. For example, "
                    "'https://jenkins.example.org/job/anchore' or https://jenkins.example.org/job/anchore/job/master' "
                    "in case of a pipeline job.",
                },
            },
        ),
    ),
    entities={
        "security_warnings": {
            "name": "security warning",
            "attributes": [cast(object, {"name": "Tag"}), *COMMON_ENTITY_ATTRIBUTES],
        },
    },
)
