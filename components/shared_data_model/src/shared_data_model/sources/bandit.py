"""Bandit source."""

from ..meta.entity import Color
from ..meta.source import Source
from ..parameters import access_parameters, MultipleChoiceParameter, Severities


ALL_BANDIT_METRICS = ["security_warnings", "source_up_to_dateness"]

BANDIT = Source(
    name="Bandit",
    description="Bandit is a tool designed to find common security issues in Python code.",
    url="https://github.com/PyCQA/bandit",
    parameters=dict(
        severities=Severities(values=["low", "medium", "high"]),
        confidence_levels=MultipleChoiceParameter(
            name="Confidence levels",
            help="If provided, only count security warnings with the selected confidence levels.",
            placeholder="all confidence levels",
            values=["low", "medium", "high"],
            metrics=["security_warnings"],
        ),
        **access_parameters(ALL_BANDIT_METRICS, source_type="Bandit report", source_type_format="JSON")
    ),
    entities=dict(
        security_warnings=dict(
            name="security warning",
            attributes=[
                dict(name="Warning", key="issue_text", url="more_info"),
                dict(name="Location"),
                dict(name="Confidence", key="issue_confidence"),
                dict(name="Severity", key="issue_severity", color=dict(High=Color.NEGATIVE, Medium=Color.WARNING)),
            ],
        ),
    ),
)
