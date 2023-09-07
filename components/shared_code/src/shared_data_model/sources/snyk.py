"""Snyk source."""

from pydantic import HttpUrl

from shared_data_model.meta.entity import Color, Entity, EntityAttribute, EntityAttributeType
from shared_data_model.meta.source import Source
from shared_data_model.parameters import Severities, access_parameters

SNYK = Source(
    name="Snyk",
    description="Snyk vulnerability report in JSON format.",
    url=HttpUrl("https://docs.snyk.io/products/snyk-code/cli-for-snyk-code/working-with-the-snyk-code-cli-results"),
    parameters={
        "severities": Severities(values=["low", "medium", "high"]),
        **access_parameters(
            ["security_warnings"],
            source_type="Snyk vulnerability report",
            source_type_format="JSON",
        ),
    },
    entities={
        "security_warnings": Entity(
            name="security warning",
            attributes=[
                EntityAttribute(name="Dependency"),
                EntityAttribute(
                    name="Number of vulnerabilities",
                    key="nr_vulnerabilities",
                    type=EntityAttributeType.INTEGER,
                ),
                EntityAttribute(name="Example vulnerability", url="url"),
                EntityAttribute(name="Example vulnerable path", key="example_path"),
                EntityAttribute(name="Highest severity", color={"high": Color.NEGATIVE, "medium": Color.WARNING}),
            ],
        ),
    },
)
