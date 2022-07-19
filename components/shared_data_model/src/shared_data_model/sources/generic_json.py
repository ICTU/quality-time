"""Generic JSON for security warnings source."""

from ..meta.entity import Color
from ..meta.source import Source
from ..parameters import access_parameters, Severities


GENERIC_JSON = Source(
    name="JSON file with security warnings",
    description="A generic vulnerability report with security warnings in JSON format.",
    url="https://quality-time.readthedocs.io/en/latest/usage.html#generic-json-format-for-security-warnings",
    parameters=dict(
        severities=Severities(values=["low", "medium", "high"]),
        **access_parameters(
            ["security_warnings"], source_type="generic vulnerability report", source_type_format="JSON"
        )
    ),
    entities=dict(
        security_warnings=dict(
            name="security warning",
            attributes=[
                dict(name="Title"),
                dict(name="Description"),
                dict(name="Severity", color=dict(high=Color.NEGATIVE, medium=Color.WARNING)),
            ],
        )
    ),
)
