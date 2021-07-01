"""OJAudit source."""

from ..meta.entity import Color, EntityAttributeType
from ..meta.source import Source
from ..parameters import access_parameters, Severities


OJAUDIT = Source(
    name="OJAudit",
    description="An Oracle JDeveloper program to audit Java code against JDeveloper's audit rules.",
    url="https://www.oracle.com/technetwork/developer-tools/jdev",
    parameters=dict(
        severities=Severities(
            help="If provided, only count violations with the selected severities.",
            values=["advisory", "incomplete", "warning", "error", "exception"],
            metrics=["violations"],
        ),
        **access_parameters(["violations"], source_type="an OJAudit report", source_type_format="XML")
    ),
    entities=dict(
        violations=dict(
            name="violation",
            attributes=[
                dict(name="Message"),
                dict(
                    name="Severity", color=dict(exception=Color.NEGATIVE, error=Color.NEGATIVE, warning=Color.WARNING)
                ),
                dict(name="Component"),
                dict(name="Number of occurrences", key="count", type=EntityAttributeType.INTEGER),
            ],
        )
    ),
)
