"""Bandit source."""

from pydantic import HttpUrl

from shared_data_model.meta.entity import Color, Entity, EntityAttribute
from shared_data_model.meta.source import Source
from shared_data_model.parameters import MultipleChoiceParameter, Severities, access_parameters

ALL_BANDIT_METRICS = ["security_warnings", "source_up_to_dateness"]

BANDIT = Source(
    name="Bandit",
    description="Bandit is a tool designed to find common security issues in Python code.",
    url=HttpUrl("https://github.com/PyCQA/bandit"),
    parameters={
        "severities": Severities(values=["low", "medium", "high"]),
        "confidence_levels": MultipleChoiceParameter(
            name="Confidence levels",
            help="If provided, only count security warnings with the selected confidence levels.",
            placeholder="all confidence levels",
            values=["low", "medium", "high"],
            metrics=["security_warnings"],
        ),
        **access_parameters(ALL_BANDIT_METRICS, source_type="Bandit report", source_type_format="JSON"),
    },
    entities={
        "security_warnings": Entity(
            name="security warning",
            attributes=[
                EntityAttribute(name="Warning", key="issue_text", url="more_info"),
                EntityAttribute(name="Location"),
                EntityAttribute(name="Confidence", key="issue_confidence"),
                EntityAttribute(
                    name="Severity",
                    key="issue_severity",
                    color={"High": Color.NEGATIVE, "Medium": Color.WARNING},
                ),
            ],
        ),
    },
)
