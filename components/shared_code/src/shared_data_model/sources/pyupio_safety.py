"""Pyupio Safety source."""

from pydantic import HttpUrl

from shared_data_model.meta.entity import Entity, EntityAttribute
from shared_data_model.meta.source import Source
from shared_data_model.parameters import access_parameters

PYUPIO_SAFETY = Source(
    name="Pyupio Safety",
    description="Safety checks Python dependencies for known security vulnerabilities.",
    url=HttpUrl("https://github.com/pyupio/safety"),
    parameters=access_parameters(["security_warnings"], source_type="Safety report", source_type_format="JSON"),
    entities={
        "security_warnings": Entity(
            name="security warning",
            attributes=[
                EntityAttribute(name="Package"),
                EntityAttribute(name="Installed"),
                EntityAttribute(name="Affected"),
                EntityAttribute(name="Vulnerability"),
            ],
        ),
    },
)
