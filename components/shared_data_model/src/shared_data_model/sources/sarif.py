"""SARIF JSON for security warnings source."""

from shared_data_model.meta.entity import Color
from shared_data_model.meta.source import Source
from shared_data_model.parameters import Severities, access_parameters

SARIF_JSON = Source(
    name="SARIF",
    description="A Static Analysis Results Interchange Format (SARIF) vulnerability report in JSON format.",
    url="https://www.oasis-open.org/committees/tc_home.php?wg_abbrev=sarif",
    parameters=dict(
        levels=Severities(
            name="Levels",
            placeholder="all levels",
            help="If provided, only count security warnings with the selected levels.",
            values=["none", "note", "warning", "error"],
        ),
        **access_parameters(["security_warnings"], source_type="SARIF vulnerability report", source_type_format="JSON"),
    ),
    entities={
        "security_warnings": {
            "name": "security warning",
            "attributes": [
                {"name": "Message"},
                {"name": "Level", "color": {"error": Color.NEGATIVE, "warning": Color.WARNING, "note": Color.ACTIVE}},
                {"name": "Locations"},
                {"name": "Rule", "url": "url"},
                {"name": "Description"},
            ],
        },
    },
)
