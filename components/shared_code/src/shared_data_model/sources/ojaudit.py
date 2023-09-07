"""OJAudit source."""

from pydantic import HttpUrl

from shared_data_model.meta.entity import Color, Entity, EntityAttribute, EntityAttributeType
from shared_data_model.meta.source import Source
from shared_data_model.parameters import Severities, access_parameters

OJAUDIT = Source(
    name="OJAudit",
    description="An Oracle JDeveloper program to audit Java code against JDeveloper's audit rules.",
    url=HttpUrl("https://www.oracle.com/application-development/technologies/jdeveloper.html"),
    parameters={
        "severities": Severities(
            help="If provided, only count violations with the selected severities.",
            values=["advisory", "incomplete", "warning", "error", "exception"],
            metrics=["violations"],
        ),
        **access_parameters(["violations"], source_type="an OJAudit report", source_type_format="XML"),
    },
    entities={
        "violations": Entity(
            name="violation",
            attributes=[
                EntityAttribute(name="Message"),
                EntityAttribute(
                    name="Severity",
                    color={"exception": Color.NEGATIVE, "error": Color.NEGATIVE, "warning": Color.WARNING},
                ),
                EntityAttribute(name="Component"),
                EntityAttribute(name="Number of occurrences", key="count", type=EntityAttributeType.INTEGER),
            ],
        ),
    },
)
