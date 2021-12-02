"""Snyk source."""

from ..meta.entity import Color, EntityAttributeType
from ..meta.source import Source
from ..parameters import access_parameters, Severities


SNYK = Source(
    name="Snyk",
    description="Snyk vulnerability report in JSON format.",
    url="https://docs.snyk.io/products/snyk-code/cli-for-snyk-code/advanced-snyk-code-cli-usage",
    parameters=dict(
        severities=Severities(values=["low", "medium", "high"]),
        **access_parameters(["security_warnings"], source_type="Snyk vulnerability report", source_type_format="JSON")
    ),
    entities=dict(
        security_warnings=dict(
            name="security warning",
            attributes=[
                dict(name="Dependency"),
                dict(name="Number of vulnerabilities", key="nr_vulnerabilities", type=EntityAttributeType.INTEGER),
                dict(name="Example vulnerability", url="url"),
                dict(name="Example vulnerable path", key="example_path"),
                dict(name="Highest severity", color=dict(high=Color.NEGATIVE, medium=Color.WARNING)),
            ],
        ),
    ),
)
