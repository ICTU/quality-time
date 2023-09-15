"""Trivy JSON source."""

from pydantic import HttpUrl

from shared_data_model.meta.entity import Color, Entity, EntityAttribute
from shared_data_model.meta.source import Source
from shared_data_model.parameters import Severities, access_parameters

TRIVY_JSON = Source(
    name="Trivy JSON",
    description="A Trivy vulnerability report in JSON format.",
    url=HttpUrl("https://aquasecurity.github.io/trivy/latest/docs/configuration/reporting/#json"),
    parameters={
        "levels": Severities(
            name="Levels",
            placeholder="all levels",
            help="If provided, only count security warnings with the selected levels.",
            values=["unknown", "low", "medium", "high", "critical"],
            metrics=["security_warnings"],
        ),
        **access_parameters(["security_warnings"], source_type="Trivy vulnerability report", source_type_format="JSON"),
    },
    entities={
        "security_warnings": Entity(
            name="security warning",
            attributes=[
                EntityAttribute(name="Vulnerability ID"),
                EntityAttribute(name="Title", url="url"),
                EntityAttribute(name="Description"),
                EntityAttribute(
                    name="Level",
                    color={"critical": Color.NEGATIVE, "high": Color.WARNING, "unknown": Color.ACTIVE},
                ),
                EntityAttribute(name="Package name"),
                EntityAttribute(name="Installed version"),
                EntityAttribute(name="Fixed version"),
            ],
        ),
    },
)
