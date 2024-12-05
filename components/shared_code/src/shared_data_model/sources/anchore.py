"""Anchore sources."""

from pydantic import HttpUrl

from shared_data_model.meta.entity import Color, Entity, EntityAttribute
from shared_data_model.meta.source import Source
from shared_data_model.parameters import URL, FixAvailability, Severities, access_parameters

from .jenkins import JENKINS_TOKEN_DOCS, jenkins_access_parameters

ALL_ANCHORE_METRICS = ["security_warnings", "source_up_to_dateness"]

SEVERITIES = Severities(values=["Unknown", "Negligible", "Low", "Medium", "High", "Critical"])

COMMON_ENTITY_ATTRIBUTES = [
    EntityAttribute(name="CVE", url="url"),
    EntityAttribute(name="Package"),
    EntityAttribute(name="Fix"),
    EntityAttribute(
        name="Severity",
        color={"Critical": Color.NEGATIVE, "High": Color.NEGATIVE, "Medium": Color.WARNING, "Low": Color.WARNING},
    ),
]

ANCHORE = Source(
    name="Anchore",
    description="Anchore image scan analysis report in JSON format.",
    url=HttpUrl("https://docs.anchore.com/current/docs/using/integration/ci_cd/inline_scanning/"),
    parameters={
        "details_url": URL(
            name="URL to an Anchore details report in JSON format or "
            "to a zip with Anchore details reports in JSON format",
            metrics=["source_up_to_dateness"],
        ),
        "severities": SEVERITIES,
        "fix_availability": FixAvailability(),
        **access_parameters(
            ALL_ANCHORE_METRICS,
            source_type="an Anchore vulnerability report",
            source_type_format="JSON",
            kwargs={"url": {"metrics": ["security_warnings"]}},
        ),
    },
    entities={
        "security_warnings": Entity(
            name="security warning",
            attributes=[EntityAttribute(name="Report filename", key="filename"), *COMMON_ENTITY_ATTRIBUTES],
        ),
    },
)

ANCHORE_JENKINS_PLUGIN = Source(
    name="Anchore Jenkins plugin",
    description="A Jenkins job with an Anchore report produced by the Anchore Jenkins plugin.",
    documentation={"security_warnings": JENKINS_TOKEN_DOCS, "source_up_to_dateness": JENKINS_TOKEN_DOCS},
    url=HttpUrl("https://plugins.jenkins.io/anchore-container-scanner/"),
    parameters={
        "severities": SEVERITIES,
        "fix_availability": FixAvailability(),
        **jenkins_access_parameters(
            ALL_ANCHORE_METRICS,
            kwargs={
                "url": {
                    "help": "URL to a Jenkins job with an Anchore report generated by the Anchore plugin. For "
                    "example, 'https://jenkins.example.org/job/anchore' or "
                    "https://jenkins.example.org/job/anchore/job/main' in case of a pipeline job.",
                },
            },
        ),
    },
    entities={
        "security_warnings": Entity(
            name="security warning",
            attributes=[EntityAttribute(name="Tag"), *COMMON_ENTITY_ATTRIBUTES],
        ),
    },
)
