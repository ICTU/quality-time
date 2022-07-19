"""Pyupio Safety source."""

from ..meta.source import Source
from ..parameters import access_parameters


PYUPIO_SAFETY = Source(
    name="Pyupio Safety",
    description="Safety checks Python dependencies for known security vulnerabilities.",
    url="https://github.com/pyupio/safety",
    parameters=access_parameters(["security_warnings"], source_type="Safety report", source_type_format="JSON"),
    entities=dict(
        security_warnings=dict(
            name="security warning",
            attributes=[
                dict(name="Package"),
                dict(name="Installed"),
                dict(name="Affected"),
                dict(name="Vulnerability"),
            ],
        ),
    ),
)
