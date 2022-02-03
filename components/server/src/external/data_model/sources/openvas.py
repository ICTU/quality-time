"""OpenVAS source."""

from ..meta.entity import Color
from ..meta.source import Source
from ..parameters import access_parameters, Severities


ALL_OPENVAS_METRICS = ["security_warnings", "source_version", "time_passed"]

OPENVAS = Source(
    name="OpenVAS",
    description="OpenVAS (Open Vulnerability Assessment System) is a software framework of several services and tools "
    "offering vulnerability scanning and vulnerability management.",
    url="https://www.openvas.org",
    parameters=dict(
        severities=Severities(values=["log", "low", "medium", "high"]),
        **access_parameters(ALL_OPENVAS_METRICS, source_type="an OpenVAS report", source_type_format="XML")
    ),
    entities=dict(
        security_warnings=dict(
            name="security warning",
            attributes=[
                dict(name="Warning", key="name"),
                dict(name="Severity", color=dict(High=Color.NEGATIVE, Medium=Color.WARNING)),
                dict(name="Description", pre=True),
                dict(name="Host"),
                dict(name="Port"),
            ],
        ),
    ),
)
