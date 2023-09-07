"""SARIF JSON for security warnings source."""

from pydantic import HttpUrl

from shared_data_model.meta.entity import Color, Entity, EntityAttribute
from shared_data_model.meta.source import Source
from shared_data_model.parameters import Severities, access_parameters

SARIF_ATTRIBUTES = [
    EntityAttribute(name="Message"),
    EntityAttribute(name="Level", color={"error": Color.NEGATIVE, "warning": Color.WARNING, "note": Color.ACTIVE}),
    EntityAttribute(name="Locations"),
    EntityAttribute(name="Rule", url="url"),
    EntityAttribute(name="Description"),
]

SARIF_JSON = Source(
    name="SARIF",
    description="A Static Analysis Results Interchange Format (SARIF) vulnerability report in JSON format.",
    url=HttpUrl("https://www.oasis-open.org/committees/tc_home.php?wg_abbrev=sarif"),
    parameters={
        "levels": Severities(
            name="Levels",
            placeholder="all levels",
            help="If provided, only count entities with the selected levels.",
            values=["none", "note", "warning", "error"],
            metrics=["security_warnings", "violations"],
        ),
        **access_parameters(
            ["security_warnings", "violations"],
            source_type="SARIF vulnerability report",
            source_type_format="JSON",
        ),
    },
    entities={
        "security_warnings": Entity(name="security warning", attributes=SARIF_ATTRIBUTES),
        "violations": Entity(name="violation", attributes=SARIF_ATTRIBUTES),
    },
)
