"""Generic JSON for security warnings source."""

from ..meta.entity import Color
from ..meta.source import Source
from ..parameters import access_parameters, Severities


DOCUMENTATION = """In some cases, there are security vulnerabilities not found by automated tools.
Quality-time has the ability to parse security warnings from JSON files with a generic format.

The JSON format consists of an object with one key `vulnerabilities`. The value should be a list of vulnerabilities.
Each vulnerability is an object with three keys: `title`, `description`, and `severity`. The title and description
values should be strings. The severity is also a string and can be either `low`, `medium`, or `high`.

Example generic JSON file:

```json
{
    "vulnerabilities": [
        {
            "title": "ISO27001:2013 A9 Insufficient Access Control",
            "description": "The Application does not enforce Two-Factor Authentication and therefore not satisfy \
                security best practices.",
            "severity": "high"
        },
        {
            "title": "Threat Model Finding: Uploading Malicious of Malicious files",
            "description": "An attacker can upload malicious files with low privileges can perform direct API calls \
                and perform unwanted mutations or see unauthorized information.",
            "severity": "medium"
        }
    ]
}
```
"""


GENERIC_JSON = Source(
    name="JSON file with security warnings",
    description="A generic vulnerability report with security warnings in JSON format.",
    documentation=dict(generic=DOCUMENTATION),
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
