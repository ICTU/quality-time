"""OpenVAS source."""

from shared_data_model.meta.entity import Color
from shared_data_model.meta.source import Source
from shared_data_model.parameters import Severities, access_parameters

ALL_OPENVAS_METRICS = ["security_warnings", "source_up_to_dateness", "source_version"]

OPENVAS = Source(
    name="OpenVAS",
    description="OpenVAS (Open Vulnerability Assessment System) is a software framework of several services and tools "
    "offering vulnerability scanning and vulnerability management.",
    url="https://www.openvas.org",
    parameters=dict(
        severities=Severities(values=["log", "low", "medium", "high"]),
        **access_parameters(ALL_OPENVAS_METRICS, source_type="an OpenVAS report", source_type_format="XML"),
    ),
    entities={
        "security_warnings": {
            "name": "security warning",
            "attributes": [
                {"name": "Warning", "key": "name"},
                {"name": "Severity", "color": {"High": Color.NEGATIVE, "Medium": Color.WARNING}},
                {"name": "Description", "pre": True},
                {"name": "Host"},
                {"name": "Port"},
            ],
        },
    },
)
