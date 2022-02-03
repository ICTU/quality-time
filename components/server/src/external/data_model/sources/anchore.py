"""Anchore sources."""

from typing import cast

from ..meta.entity import Color
from ..meta.source import Source
from ..parameters import access_parameters, Severities, URL

from .jenkins import jenkins_access_parameters


ALL_ANCHORE_METRICS = ["security_warnings", "time_passed"]

SEVERITIES = Severities(values=["Unknown", "Negligible", "Low", "Medium", "High", "Critical"])

COMMON_ENTITY_ATTRIBUTES = [
    dict(name="CVE", url="url"),
    dict(name="Package"),
    dict(name="Fix"),
    dict(
        name="Severity",
        color=dict(Critical=Color.NEGATIVE, High=Color.NEGATIVE, Medium=Color.WARNING, Low=Color.WARNING),
    ),
]

ANCHORE = Source(
    name="Anchore",
    description="Anchore image scan analysis report in JSON format.",
    url="https://docs.anchore.com/current/docs/using/integration/ci_cd/inline_scanning/",
    parameters=dict(
        details_url=URL(
            name="URL to an Anchore details report in JSON format or "
            "to a zip with Anchore details reports in JSON format",
            metrics=["time_passed"],
        ),
        severities=SEVERITIES,
        **access_parameters(
            ALL_ANCHORE_METRICS,
            source_type="an Anchore vulnerability report",
            source_type_format="JSON",
            kwargs=dict(url=dict(metrics=["security_warnings"])),
        ),
    ),
    entities=dict(
        security_warnings=dict(
            name="security warning",
            attributes=[cast(object, dict(name="Report filename", key="filename"))] + COMMON_ENTITY_ATTRIBUTES,
        )
    ),
)

ANCHORE_JENKINS_PLUGIN = Source(
    name="Anchore Jenkins plugin",
    description="A Jenkins job with an Anchore report produced by the Anchore Jenkins plugin.",
    url="https://plugins.jenkins.io/anchore-container-scanner/",
    parameters=dict(
        severities=SEVERITIES,
        **jenkins_access_parameters(
            ALL_ANCHORE_METRICS,
            kwargs=dict(
                url=dict(
                    help="URL to a Jenkins job with an Anchore report generated by the Anchore plugin. For example, "
                    "'https://jenkins.example.org/job/anchore' or https://jenkins.example.org/job/anchore/job/master' "
                    "in case of a pipeline job."
                )
            ),
        ),
    ),
    entities=dict(
        security_warnings=dict(
            name="security warning", attributes=[cast(object, dict(name="Tag"))] + COMMON_ENTITY_ATTRIBUTES
        )
    ),
)
