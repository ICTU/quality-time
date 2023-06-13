"""Snyk source."""

from shared_data_model.meta.entity import Color, EntityAttributeType
from shared_data_model.meta.source import Source
from shared_data_model.parameters import Severities, access_parameters

SNYK = Source(
    name="Snyk",
    description="Snyk vulnerability report in JSON format.",
    url="https://docs.snyk.io/products/snyk-code/cli-for-snyk-code/working-with-the-snyk-code-cli-results",
    parameters=dict(
        severities=Severities(values=["low", "medium", "high"]),
        **access_parameters(["security_warnings"], source_type="Snyk vulnerability report", source_type_format="JSON"),
    ),
    entities={
        "security_warnings": {
            "name": "security warning",
            "attributes": [
                {"name": "Dependency"},
                {"name": "Number of vulnerabilities", "key": "nr_vulnerabilities", "type": EntityAttributeType.INTEGER},
                {"name": "Example vulnerability", "url": "url"},
                {"name": "Example vulnerable path", "key": "example_path"},
                {"name": "Highest severity", "color": {"high": Color.NEGATIVE, "medium": Color.WARNING}},
            ],
        },
    },
)
