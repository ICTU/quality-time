"""Pyupio Safety source."""

from shared_data_model.meta.source import Source
from shared_data_model.parameters import access_parameters

PYUPIO_SAFETY = Source(
    name="Pyupio Safety",
    description="Safety checks Python dependencies for known security vulnerabilities.",
    url="https://github.com/pyupio/safety",
    parameters=access_parameters(["security_warnings"], source_type="Safety report", source_type_format="JSON"),
    entities={
        "security_warnings": {
            "name": "security warning",
            "attributes": [
                {"name": "Package"},
                {"name": "Installed"},
                {"name": "Affected"},
                {"name": "Vulnerability"},
            ],
        },
    },
)
